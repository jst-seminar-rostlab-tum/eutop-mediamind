import asyncio
import json
import uuid
from datetime import date, datetime
from typing import Sequence

from app.core.logger import get_logger
from app.models.article import Article
from app.repositories.article_repository import ArticleRepository
from app.repositories.entity_repository import ArticleEntityRepository
from app.services.llm_service.llm_client import LLMClient
from app.services.llm_service.llm_models import LLMModels

logger = get_logger(__name__)


class ArticleSummaryService:
    _semaphore = asyncio.Semaphore(50)
    _llm_client = LLMClient(LLMModels.openai_4o)

    @staticmethod
    def _build_prompt(article: Article) -> str:
        return (
            f"Summarize the following article in a clear, neutral, "
            f"and informative tone, covering all major points without "
            f"omitting key details. "
            f"Then, extract and list separately:\n"
            f"- Persons mentioned\n"
            f"- Industries mentioned\n"
            f"- Events mentioned\n"
            f"- Organizations mentioned\n"
            f"- Citations in academic reference format present in the text\n"
            f"\nArticle content:\n{article.content}\n\n"
            f"Return your answer as a JSON object with the "
            f"following structure:\n"
            f"{{\n"
            f'  "summary": "<summary text>",\n'
            f'  "persons": ["person1", "person2", ...],\n'
            f'  "industries": ["industry1", "industry2", ...],\n'
            f'  "events": ["event1", "event2", ...],\n'
            f'  "organizations": ["org1", "org2", ...],\n'
            f'  "citations": ["cit1", "cit2", ...]\n'
            f"}}\n"
            f"Make sure the JSON is valid and parsable."
        )

    @staticmethod
    def _generate_summary_batch_file(
        articles: Sequence[Article],
    ) -> str | None:
        """
        Generates a .jsonl batch file containing prompts for summarizing
        and entity extraction.

        Args:
            articles (Sequence[Article]): A list of articles to summarize
            and extract entities.

        Returns:
            str | None: The path to the generated .jsonl batch file.
        """
        custom_ids = [str(article.id) for article in articles]
        prompts = [
            ArticleSummaryService._build_prompt(article)
            for article in articles
        ]

        batch_path = LLMClient.generate_batch(
            custom_ids=custom_ids,
            prompts=prompts,
            model=LLMModels.openai_4o.value,
            temperature=0.1,
            output_filename="summary_batch.jsonl",
        )

        if not batch_path:
            return None

        return batch_path

    @staticmethod
    async def _process_and_store(article_id: uuid.UUID, content: str) -> None:
        """
        Parses content and stores summary and extracted entities.

        Args:
            article_id (UUID): ID of the article being processed.
            content (str): JSON-formatted response from the llm model.
        """
        try:
            if content.startswith("```json"):
                content = content[len("```json"):].strip()
            if content.endswith("```"):
                content = content[:-len("```")].strip()

            data = json.loads(content)

            summary = data.get("summary", "")
            persons = data.get("persons", [])
            industries = data.get("industries", [])
            events = data.get("events", [])
            organizations = data.get("organizations", [])
            citations = data.get("citations", [])

            await ArticleRepository.update_article_summary(article_id, summary)
            await ArticleEntityRepository.add_entities(
                article_id,
                persons=persons,
                industries=industries,
                events=events,
                organizations=organizations,
                citations=citations,
            )
        except Exception as e:
            logger.error(
                f"Error processing and storing article {article_id}: {e}"
            )

    @staticmethod
    async def _summarize_and_store_batch(articles: Sequence[Article]) -> None:
        batch_path = ArticleSummaryService._generate_summary_batch_file(
            articles=articles,
        )
        if not batch_path:
            logger.error("Could not generate batch file")
            return

        output_lines = await LLMClient.run_batch_api(str(batch_path))

        if not output_lines:
            logger.error("Could not obtain results from batch output")
            return

        for line in output_lines:
            try:
                result = json.loads(line)
                article_id = uuid.UUID(result["custom_id"])
                response = result["response"]
                content = response["body"]["choices"][0]["message"]["content"]
                await ArticleSummaryService._process_and_store(
                    article_id, content
                )
            except Exception as e:
                logger.error(f"Error storing data for line: {e}")

    @staticmethod
    async def _summarize_and_store_concurrently(article: Article) -> None:
        prompt = ArticleSummaryService._build_prompt(article)
        async with ArticleSummaryService._semaphore:
            try:
                content = await asyncio.to_thread(
                    ArticleSummaryService._llm_client.generate_response, prompt
                )
                await ArticleSummaryService._process_and_store(
                    article.id, content
                )
            except Exception as e:
                logger.error(
                    f"Error summarizing article {article.id} concurrently: {e}"
                )

    @staticmethod
    async def run(
        page_size: int = 300,
        datetime_start: datetime = datetime.combine(
            date.today(), datetime.min.time()
        ),
        datetime_end: datetime = datetime.now(),
        use_batch_api: bool = False
    ) -> None:
        """
        Main entry point to summarize a list of articles and
        store their extracted entities.
        """
        while True:
            articles = await ArticleRepository.list_articles_without_summary(
                limit=page_size,
                datetime_start=datetime_start,
                datetime_end=datetime_end,
            )
            if not articles:
                logger.info("No more articles to summarize")
                break

            if use_batch_api:
                logger.info(f"Processing batch with {len(articles)} articles")
                await ArticleSummaryService._summarize_and_store_batch(
                    articles
                )

            else:
                logger.info(
                    f"Processing {len(articles)} articles concurrently"
                )
                tasks = [
                    ArticleSummaryService._summarize_and_store_concurrently(
                        article
                    )
                    for article in articles
                ]
                await asyncio.gather(*tasks, return_exceptions=True)
