import uuid
import json
import time
from pathlib import Path
from typing import Optional

from openai import OpenAI
from langdetect import detect
from starlette.concurrency import run_in_threadpool

from app.core.config import configs
from app.core.logger import get_logger
from app.models.article import Article
from app.repositories.article_repository import ArticleRepository

logger = get_logger(__name__)
client_openai = OpenAI(api_key=configs.OPENAI_API_KEY)


class ArticleTranslationService:
    @staticmethod
    def translate_with_llm(content: str, target_lang: str) -> str:
        """
        Translates content to the target language using a language model.

        Args:
            content (str): The text to translate.
            target_lang (str): The target language.

        Returns:
            str: The translated text.
        """
        response = client_openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional translator. Translate "
                        f"the following text to {target_lang}, "
                        "without adding or removing meaning. Do not "
                        "assume facts not present in the original "
                        "text. Keep the translation as neutral and "
                        "faithful as possible."
                    )
                },
                {"role": "user", "content": content}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content

    @staticmethod
    def generate_translations(content: str) -> dict[str, str]:
        """
        Generates english and/or german translations of the given content
        by calling the translate_with_llm() function only if necessary

        Args:
            content (str): The text to translate.

        Returns:
            dict[str, str]: A dictionary with the translations.
        """
        if not content or content.strip() == "":
            return {"en": "", "de": ""}
        try:
            detected_lang = detect(content)
            result = {"en": "", "de": ""}

            if detected_lang != "en":
                result["en"] = ArticleTranslationService.translate_with_llm(
                    content, "English"
                )

            if detected_lang != "de":
                result["de"] = ArticleTranslationService.translate_with_llm(
                    content, "German"
                )

            return result
        except Exception as e:
            logger.error(f"OpenAI translation error: {e}")
            return {"en": "", "de": ""}

    @staticmethod
    async def translate_and_store(article_id: uuid.UUID) -> Optional[Article]:
        """
        Fetches an Article by ID, translates its content,
        and updates the translated fields in the database.
        Args:
            article_id (uuid.UUID): id of the article to translate.

        Returns:
            Optional[Article]: The updated Article object.
        """
        article = await ArticleRepository.get_article_by_id(article_id)
        if not article:
            return None

        translations = await run_in_threadpool(
            ArticleTranslationService.generate_translations, article.content
        )

        return await ArticleRepository.update_article_translations(
            article_id,
            en=translations["en"],
            de=translations["de"]
        )

    @staticmethod
    def build_request_jsonl(
        article_id: uuid.UUID, lang_code: str,
        target_lang: str, content: str
    ) -> dict:
        """
        Builds a JSONL-formatted request payload for translating
        using OpenAI's batch API.

        Args:
            article_id (uuid.UUID): id of the article being translated.
            custom_suffix (str): language code of the target language.
            target_lang (str): the target language for translation.
            content (str): the text content to be translated.

        Returns:
            dict: A dictionary representing a single JSONL entry.
        """
        return {
            "custom_id": f"{article_id}_{lang_code}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a professional translator. Translate "
                            f"the following text to {target_lang}, "
                            "without adding or removing meaning. Do not "
                            "assume facts not present in the original "
                            "text. Keep the translation as neutral and "
                            "faithful as possible."
                        )
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                "temperature": 0.1
            }
        }

    @staticmethod
    async def generate_batch_jsonl(limit: int = 50) -> str:
        """
        Generates a .jsonl file with batch translation requests
        for OpenAI Batch API.
        Args:
            limit (int, optional): the maximum number of articles to process
            for the batch.

        Returns:
            str: The path to the generated JSONL file.
        """
        articles = await ArticleRepository.get_sameple_articles(limit=limit)
        lines = []

        for article in articles:
            if not article.content:
                continue
            detected_lang = detect(article.content)
            if detected_lang != "en":
                line = ArticleTranslationService.build_request_jsonl(
                    article.id, "en", "English", article.content
                )
                lines.append(line)
            if detected_lang != "de":
                line = ArticleTranslationService.build_request_jsonl(
                    article.id, "de", "German", article.content
                )
                lines.append(line)

        output_path = Path("openai_batch_translation.jsonl")
        with output_path.open("w", encoding="utf-8") as f:
            for line in lines:
                f.write(json.dumps(line, ensure_ascii=False) + "\n")

        logger.info(
            (
                "Batch for translation (JSONL) generated with "
                f"{len(lines)} requests"
            )
        )
        return str(output_path)

    @staticmethod
    def upload_batch_file(jsonl_path: str):
        """
        Uploads a .jsonl file (batch) to OpenAI for use with the batch API.

        Args:
            jsonl_path (str): path to the .jsonl file containing
            batch requests.

        Returns:
            File: the uploaded OpenAI file object.
        """
        with open(jsonl_path, "rb") as f:
            file = client_openai.files.create(file=f, purpose="batch")
        logger.info(f"Translation batch uploaded to OpenAI: {file.id}")
        return file

    @staticmethod
    def create_batch_job(file_id: str):
        """
        Creates a new batch job in OpenAI using the uploaded file ID.

        Args:
            file_id (str): The ID of the uploaded .jsonl file containing
            the batch translation requests.

        Returns:
            Batch: The created OpenAI batch job object.
        """
        batch = client_openai.batches.create(
            input_file_id=file_id,
            endpoint="/v1/chat/completions",
            completion_window="24h"
        )
        logger.info(f"Batch work created: {batch.id}")
        return batch

    @staticmethod
    def wait_for_batch_completion(batch_id: str) -> bool:
        """
        Checks the status of a batch job until it
        finalizes (with error or not).

        Args:
            batch_id (str): The ID of the batch job to monitor.

        Returns:
            bool: True if the batch was completed successfully,
            False otherwise.
        """
        while True:
            current = client_openai.batches.retrieve(batch_id)
            logger.info(f"Batch status: {current.status}")
            if current.status in (
                "completed", "failed", "expired", "cancelled"
            ):
                break
            time.sleep(10)
        return current.status == "completed"

    @staticmethod
    async def process_batch_output(batch_id: str) -> list[Article]:
        """
        Processes the output of a completed OpenAI batch translation job.

        Args:
            batch_id (str): The ID of the completed batch job.

        Returns:
            list[Article]: A list of articles that were successfully updated
            with translations.
        """
        current = client_openai.batches.retrieve(batch_id)
        file_response = client_openai.files.content(current.output_file_id)
        lines = file_response.text.strip().splitlines()

        updated_articles = []
        for line in lines:
            try:
                parsed = json.loads(line)
                custom_id = parsed.get("custom_id")
                response = parsed.get("response")

                if not response:
                    continue

                # Extract article id and language code from custom_id
                article_id_str, lang_code = custom_id.rsplit("_", 1)
                article_id = uuid.UUID(article_id_str)

                content = response["body"]["choices"][0]["message"]["content"]

                article = await ArticleRepository.update_article_translations(
                    article_id, **{lang_code: content}
                )
                logger.info(
                    f"Article {article_id} updated with "
                    f"{lang_code} translation"
                )
                updated_articles.append(article)

            except Exception as e:
                logger.exception(f"Error at processing line from batch: {e}")

        return updated_articles

    @staticmethod
    async def run_translate_with_batch_api(limit: int = 50) -> list[Article]:
        """
        Translates multiple articles' content into english and/or german
        using the OpenAI Batch API.

        Args:
            limit (int, optional): the maximum number of articles to include
            in the batch.

        Returns:
            list[Article]: A list of updated Article objects
        """
        jsonl_path = await ArticleTranslationService.generate_batch_jsonl(
            limit=limit
        )
        file = ArticleTranslationService.upload_batch_file(jsonl_path)
        batch = ArticleTranslationService.create_batch_job(file.id)

        if not ArticleTranslationService.wait_for_batch_completion(batch.id):
            logger.error(f"The batch was not completed: {batch.id}")
            return

        return await ArticleTranslationService.process_batch_output(batch.id)
