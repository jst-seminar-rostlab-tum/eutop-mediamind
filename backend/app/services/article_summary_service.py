import uuid
from typing import Optional, Sequence

from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import ChatOpenAI
from starlette.concurrency import run_in_threadpool

from app.core.config import configs
from app.core.logger import get_logger
from app.models.article import Article
from app.repositories.article_repository import ArticleRepository

logger = get_logger(__name__)


class ArticleSummaryService:
    @staticmethod
    def summarize_text(text: str) -> str:
        """
        Summarizes the given text using a language model.

        Args:
            text (str): The text to summarize.

        Returns:
            str: The summarized text.
        """
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=configs.OPENAI_API_KEY,
        )

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_text(text)
        docs = [Document(page_content=t) for t in texts]

        chain = load_summarize_chain(llm, chain_type="map_reduce")
        summary = chain.invoke(docs)
        return summary["output_text"]

    @staticmethod
    async def summarize_and_store(article_id: uuid.UUID) -> Optional[Article]:
        """
        Fetches an Article by ID, generates a summary for its content,
        and updates only the `summary` field in the database.

        Returns:
            The updated Article if it exists, otherwise None.
        """
        article = await ArticleRepository.get_article_by_id(article_id)

        if not article:
            return None

        summary = ArticleSummaryService.summarize_text(article.content)
        return await ArticleRepository.update_article_summary(
            article_id, summary
        )

    @staticmethod
    async def run(page_size: int = 100) -> None:
        """
        Fetches all articles without a summary in batches,
        generates summaries for each,
        and updates the `summary` field in the database.

        Args:
            page_size (int): Number of articles to process in each batch.
        """
        page = 0
        offset = page * page_size

        articles: Sequence[Article] = (
            await ArticleRepository.list_articles_without_summary(
                limit=page_size, offset=offset
            )
        )

        while articles:
            logger.info(
                f"Processing page {page + 1} with {len(articles)} articles"
            )
            for article in articles:
                try:
                    # Run in a threadpool to avoid blocking the event loop
                    summary = await run_in_threadpool(
                        ArticleSummaryService.summarize_text, article.content
                    )
                    await ArticleRepository.update_article_summary(
                        article.id, summary
                    )
                    logger.info(f"Updated summary for article {article.id}")

                except Exception:
                    continue

            page += 1
            offset = page * page_size

            articles = await ArticleRepository.list_articles_without_summary(
                limit=page_size, offset=offset
            )
