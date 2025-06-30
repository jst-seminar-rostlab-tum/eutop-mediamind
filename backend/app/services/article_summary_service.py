import json
import uuid
from datetime import date
from typing import Sequence

from app.core.logger import get_logger
from app.models.article import Article
from app.repositories.article_repository import ArticleRepository
from app.repositories.entity_repository import ArticleEntityRepository
from app.services.llm_service.llm_client import LLMClient
from app.services.llm_service.llm_models import LLMModels

logger = get_logger(__name__)


class ArticleSummaryService:

    @staticmethod
    def build_prompt(article: Article) -> str:
        return (
            f"Summarize the following article in a clear, neutral, "
            f"and informative tone, covering all major points without "
            f"omitting key details. "
            f"Then, extract and list separately:\n"
            f"- Persons mentioned\n"
            f"- Industries mentioned\n"
            f"- Events mentioned\n"
            f"- Organizations mentioned\n"
            f"Article content:\n{article.content}\n\n"
            f"Return your answer as a JSON object with the"
            f"following structure:\n"
            f"{{\n"
            f'  "summary": "<summary text>",\n'
            f'  "persons": ["person1", "person2", ...],\n'
            f'  "industries": ["industry1", "industry2", ...],\n'
            f'  "events": ["event1", "event2", ...],\n'
            f'  "organizations": ["org1", "org2", ...]\n'
            f"}}\n"
            f"Make sure the JSON is valid and parsable."
        )

    @staticmethod
    def generate_summary_batch_file(
        articles: Sequence[Article],
        model: str,
        temperature: float = 0.1,
        output_filename: str = "summary_batch.jsonl",
    ) -> str | None:
        """
        Generates a .jsonl batch file containing prompts for summarizing
        and entity extraction.

        Args:
            articles (Sequence[Article]): A list of articles to summarize
            and extract entities.
            model (str): The llm model to use.
            temperature (float): The temperature setting for the model.
            output_filename (str): Filename for the output batch file.

        Returns:
            str | None: The path to the generated .jsonl batch file.
        """
        custom_ids = [str(article.id) for article in articles]
        prompts = [
            ArticleSummaryService.build_prompt(article) for article in articles
        ]

        batch_path = LLMClient.generate_batch(
            custom_ids=custom_ids,
            prompts=prompts,
            model=model,
            temperature=temperature,
            output_filename=output_filename,
        )

        if not batch_path:
            logger.error("Could not generate .jsonl batch file")
            return None

        return batch_path

    @staticmethod
    async def store_summaries_and_entities(output_lines: list[str]) -> None:
        """
        Parses and stores summaries and extracted entities
        from the batch model responses.

        Args:
            output_lines (list[str]): list of JSON-formatted strings,
            each representing a model output.
        """
        for line in output_lines:
            try:
                result = json.loads(line)
                article_id = uuid.UUID(result["custom_id"])
                response = result["response"]
                content = response["body"]["choices"][0]["message"]["content"]
                if content.startswith("```json"):
                    content = content[len("```json") :].strip()
                if content.endswith("```"):
                    content = content[: -len("```")].strip()
                data = json.loads(content)

                summary = data.get("summary", "")
                persons = data.get("persons", [])
                industries = data.get("industries", [])
                events = data.get("events", [])
                organizations = data.get("organizations", [])

            except Exception as e:
                logger.error(f"Error parsing summary and entities: {e}")
                continue

            try:
                await ArticleRepository.update_article_summary(
                    article_id, summary
                )
            except Exception as e:
                logger.error(
                    f"Error updating article summary for {article_id}: {e}"
                )
            try:
                await ArticleEntityRepository.add_entities(
                    article_id,
                    persons=persons,
                    industries=industries,
                    events=events,
                    organizations=organizations,
                )
            except Exception as e:
                logger.error(
                    f"Error adding entities for article {article_id}: {e}"
                )

    @staticmethod
    async def run(
        page_size: int = 100,
        date_start: date = date.today(),
        date_end: date = date.today(),
    ) -> None:
        """
        Main entry point to summarize a list of articles and
        store their extracted entities.

        Args:
            articles (list[Article]): a list of Article objects to process.
        """

        while True:
            articles = await ArticleRepository.list_articles_without_summary(
                limit=page_size,
                date_start=date_start,
                date_end=date_end,
            )
            if not articles:
                break

            logger.info(f"Processing batch with {len(articles)} articles")

            batch_path = ArticleSummaryService.generate_summary_batch_file(
                articles=articles,
                model=LLMModels.openai_4o.value,
                temperature=0.1,
                output_filename="summary_batch.jsonl",
            )
            if not batch_path:
                return

            output_lines = await LLMClient.run_batch_api(str(batch_path))

            if not output_lines:
                logger.error("Could not obtain results from batch output")
                return

            await ArticleSummaryService.store_summaries_and_entities(
                output_lines
            )
