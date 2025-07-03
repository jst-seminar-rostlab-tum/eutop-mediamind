import asyncio
import gettext

# import json
import os
import uuid
from datetime import date, datetime
from typing import Callable

from langdetect import detect

from app.core.logger import get_logger
from app.repositories.article_repository import ArticleRepository
from app.repositories.entity_repository import ArticleEntityRepository
from app.services.llm_service.llm_client import LLMClient, LLMModels

logger = get_logger(__name__)
base_prompt = (
    "You are a professional translator. Translate "
    "the following text to {target_lang}, "
    "without adding or removing meaning. Do not "
    "assume facts not present in the original "
    "text. Keep the translation as neutral and "
    "faithful as possible. If the input is a single word "
    "already in {target_lang}, just return "
    "the word as is:\n\n{content}"
)


class ArticleTranslationService:
    _translators_cache = {}
    _llm_client = LLMClient(LLMModels.openai_4o)
    _semaphore = asyncio.Semaphore(50)

    _completed_count = 0
    _completed_count_lock = asyncio.Lock()

    @staticmethod
    def get_translator(language: str) -> Callable[[str], str]:
        """
        Returns the gettext translator function for the given language.

        Args:
            language (str): language code

        Returns:
            Callable[[str], str]: a function that receives a string
            (translation key) and returns its translated string in the
            specified language. If no translation is available, it returns
            the original string.
        """
        if language not in ArticleTranslationService._translators_cache:
            locale_dir = os.path.join(os.path.dirname(__file__), "locales")
            lang = gettext.translation(
                "translations",
                localedir=locale_dir,
                languages=[language],
                fallback=True,
            )
            ArticleTranslationService._translators_cache[language] = (
                lang.gettext
            )

        return ArticleTranslationService._translators_cache[language]

    @staticmethod
    async def _process_fields(items, field_name):
        """
        Prepares the specified field from a list of items for translation.

        Args:
            items (list): List of objects to translate
            field_name: Specific field of the item to translate

        Returns:
            tuple[list[str], list[str]]: A tuple containing:
                - all_ids: List of identifiers in format "itemID_fieldName"
                - all_texts: List of corresponding text values
        """
        all_ids = []
        all_texts = []

        for item in items:
            all_ids.append(f"{item.id}_{field_name}")
            all_texts.append(getattr(item, field_name))

        return all_ids, all_texts

    @staticmethod
    def _prepare_translation_batch(
        ids: list[str], texts: list[str]
    ) -> tuple[list[str], list[str], list[dict]]:
        """
        Prepares prompts and auto-responses for a translation batch.

        Args:
            ids (list[str]): unique identifiers for each text.
            texts (list[str]): list of raw texts to translate.

        Returns:
            tuple: A tuple containing:
            - custom_ids (list[str]): IDs for requests that require
              translation.
            - prompts (list[str]): Prompts to send to the LLM.
            - auto_responses (list[dict]): Pre-filled responses for texts
              already in the target language.
        """
        if len(ids) != len(texts):
            logger.error("ids and texts must have the same length")
            return [], [], []

        target_langs = {"en": "English", "de": "German"}
        custom_ids, prompts, auto_responses = [], [], []

        for id_, text in zip(ids, texts):
            if not text or not text.strip():
                logger.warning(f"Empty text for id {id_}, skipping.")
                continue
            detected_lang = detect(text)

            for lang_code, lang_name in target_langs.items():
                full_id = f"{id_}_{lang_code}"
                if detected_lang == lang_code:
                    auto_responses.append(
                        {
                            "custom_id": full_id,
                            "response": {
                                "body": {
                                    "choices": [{"message": {"content": text}}]
                                }
                            },
                        }
                    )
                else:
                    prompts.append(
                        base_prompt.format(target_lang=lang_name, content=text)
                    )
                    custom_ids.append(full_id)

        return custom_ids, prompts, auto_responses

    @staticmethod
    async def _translate_one(custom_id, prompt):
        try:
            async with ArticleTranslationService._semaphore:
                content = await asyncio.to_thread(
                    ArticleTranslationService._llm_client.generate_response,
                    prompt,
                )

            async with ArticleTranslationService._completed_count_lock:
                ArticleTranslationService._completed_count += 1
            if ArticleTranslationService._completed_count % 50 == 0:
                logger.info(
                    f"Completed {ArticleTranslationService._completed_count} "
                    f"translation calls."
                )

            return {
                "custom_id": custom_id,
                "response": {
                    "body": {"choices": [{"message": {"content": content}}]}
                },
            }
        except Exception as e:
            logger.exception(f"Translation failed for {custom_id}: {e}")
            return None

    @staticmethod
    async def _execute_concurrent_translations(
        custom_ids: list[str], prompts: list[str], auto_responses: list[dict]
    ) -> list[dict]:
        """
        Executes the translation process with concurrent calls and
        combines results.

        Args:
            custom_ids (list[str]): identifiers for the translation requests.
            prompts (list[str]): prompts to send to the model.
            auto_responses (list[dict]): responses for texts already in the
            target language.

        Returns:
            list[dict]: All responses, including LLM completions
            and auto-responses.
        """
        tasks = [
            ArticleTranslationService._translate_one(cid, prompt)
            for cid, prompt in zip(custom_ids, prompts)
        ]
        llm_responses = await asyncio.gather(*tasks)

        return [r for r in llm_responses if r] + auto_responses

    @staticmethod
    async def _translate_all_fields(ids: list[str], texts: list[str]):
        """
        Translates all texts from the input using the batch API

        Args:
            ids (list[str]): unique identifiers for each text.
            texts (list[str]): list of raw texts to translate.

        Returns:
            list[dict]: List of translation responses.
        """
        custom_ids, prompts, auto_responses = (
            ArticleTranslationService._prepare_translation_batch(ids, texts)
        )
        responses = (
            await ArticleTranslationService._execute_concurrent_translations(
                custom_ids, prompts, auto_responses
            )
        )

        return responses

    @staticmethod
    async def _parse_translation_responses(responses):
        """
        Parses a list of translation responses from a batch API request
        and organizes them into a nested dictionary structure.

        Args:
            responses (List[Dict]): responses from the batch API

        Returns:
            Dict[UUID, Dict[str, Dict[str, str]]]: A nested dictionary
            structured as:
                {
                    object_id (UUID): {
                        lang (str): {
                            field (str): translated_content (str)
                        }
                    }
                }
        """
        translations_map = {}

        for parsed in responses:
            try:
                custom_id = parsed.get("custom_id")
                response = parsed.get("response")

                if not custom_id or not response:
                    continue

                parts = custom_id.split("_")
                if len(parts) != 3:
                    logger.warning(f"Invalid custom_id format: {custom_id}")
                    continue

                object_id_str = parts[0]
                field = parts[1]
                lang = parts[2]
                object_id = uuid.UUID(object_id_str)
                content = response["body"]["choices"][0]["message"]["content"]

                if object_id not in translations_map:
                    translations_map[object_id] = {}

                if lang not in translations_map[object_id]:
                    translations_map[object_id][lang] = {}

                translations_map[object_id][lang][field] = content

            except Exception as e:
                logger.exception(f"Error processing batch response: {e}")

        return translations_map

    @staticmethod
    async def _store_translations(translations_map, repository):
        """
        Stores translation responses back into the database.

        Args:
            translations_map (dict): Dictionary with
            structure {id: {lang: {field: value}}}
            repository: Repository class with update method
        """
        for object_id, langs in translations_map.items():
            for lang_code, fields in langs.items():
                translated_fields = {
                    f"{field}_{lang_code}": value
                    for field, value in fields.items()
                }
                await repository.update_translations(
                    object_id, **translated_fields
                )

    @staticmethod
    async def run(
        page_size: int = 300,
        datetime_start: datetime = datetime.combine(
            date.today(), datetime.min.time()
        ),
        datetime_end: datetime = datetime.now(),
    ):
        """
        Orchestrates the full articles translation pipeline in batches.

        Args:
            limit (int, optional): Number of articles to process per batch.
        """
        try:
            page = 0

            articles = (
                await ArticleRepository.get_articles_without_translations(
                    limit=page_size,
                    datetime_start=datetime_start,
                    datetime_end=datetime_end,
                )
            )
            while articles:
                logger.info(
                    f"Translating page {page + 1} with "
                    f"{len(articles)} articles"
                )

                article_ids = []
                article_texts = []
                fields_to_translate = ["title", "content", "summary"]
                for field in fields_to_translate:
                    ids, texts = (
                        await ArticleTranslationService._process_fields(
                            articles, field
                        )
                    )
                    article_ids.extend(ids)
                    article_texts.extend(texts)

                responses = (
                    await ArticleTranslationService._translate_all_fields(
                        article_ids, article_texts
                    )
                )
                if not responses:
                    logger.error(f"Translation failed for page {page + 1}")
                    break

                parse = ArticleTranslationService._parse_translation_responses
                articles_map = await parse(responses)

                await ArticleTranslationService._store_translations(
                    articles_map, ArticleRepository
                )

                page += 1

                articles = (
                    await ArticleRepository.get_articles_without_translations(
                        limit=page_size,
                        datetime_start=datetime_start,
                        datetime_end=datetime_end,
                    )
                )
            logger.info("No more articles without translation found")

        except Exception as e:
            logger.exception(f"Error running translation workflow: {e}")
            return None

    @staticmethod
    async def run_for_entities(limit: int = 100):
        """
        Orchestrates the full entity translation pipeline in batches.

        Args:
            limit (int, optional): Number of entities to process per batch.
        """
        try:
            page = 0
            offset = 0

            get = ArticleEntityRepository.get_entities_without_translations
            entities = await get(limit=limit, offset=offset)

            while entities:
                logger.info(
                    f"Translating page {page + 1} with "
                    f"{len(entities)} entities"
                )

                entity_ids, entity_texts = (
                    await ArticleTranslationService._process_fields(
                        entities, "value"
                    )
                )

                responses = (
                    await ArticleTranslationService._translate_all_fields(
                        entity_ids, entity_texts
                    )
                )

                if not responses:
                    logger.error(f"Translation failed for page {page + 1}")
                    break

                parse = ArticleTranslationService._parse_translation_responses
                entities_map = await parse(responses)

                await ArticleTranslationService._store_translations(
                    entities_map, ArticleEntityRepository
                )

                page += 1
                offset = page * limit

                entities = await get(limit=limit, offset=offset)

            logger.info("No more entities without translation found")

        except Exception as e:
            logger.exception(f"Error running entity translation workflow: {e}")
            return None
