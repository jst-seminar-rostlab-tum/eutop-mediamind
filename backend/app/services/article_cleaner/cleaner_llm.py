import asyncio
import logging
import re
from asyncio import Semaphore
from datetime import date
from typing import Optional, Tuple

import tenacity
from app.services.llm_service.llm_client import LLMClient
from app.services.llm_service.llm_models import LLMModels
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import configs
from app.models.article import Article
from app.repositories.article_repository import ArticleRepository

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# SQLAlchemy async session setup
engine = create_async_engine(str(configs.SQLALCHEMY_DATABASE_URI), echo=True)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


def remove_formatting_marks(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # bold
    text = re.sub(r"\*(.*?)\*", r"\1", text)  # italics
    text = re.sub(r"#+\s+", "", text)  # markdown headers
    text = re.sub(r"^-{3,}$", "", text, flags=re.MULTILINE)  # horizontal lines
    text = re.sub(r"\[.*?\]\(.*?\)", "", text)  # markdown links
    text = re.sub(r"\s{2,}", " ", text)  # extra spaces
    return text.strip()


class ArticleCleaner:
    def __init__(self, max_concurrency: int = 50):
        assert configs.OPENAI_API_KEY, "Missing OPENAI_API_KEY"
        self.llm_client = LLMClient(LLMModels.openai_4o)
        self.semaphore = Semaphore(max_concurrency)

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3), wait=tenacity.wait_fixed(2)
    )
    def _call_llm_sync(self, prompt: str) -> str:
        return self.llm_client.generate_response(prompt)
    
    async def clean_with_llm_removal_only(self, text, title: str) -> str:
        prompt = (
            "The following news article contains unwanted "
            "formatting artifacts "
            "such as markdown symbols (**bold**, *italic*, footnotes), author "
            "lines, inline references, and other structural noise.\n"
            "Your task is to remove noise, for example:\n"
            "Formatting marks, links, metadata, stylistic clutter and "
            "duplicated content.\n"
            "Remove duplicate title inside the body. If the first sentence is "
            "semantically very similar to the title, even with minor "
            "rewordings, remove it.\n"
            "Do not paraphrase or add any new content. Only remove noise.\n"
            "Don't change the language of the article, it should remain the "
            "same as the original.\n"
            "Return only the cleaned body text, properly structured in "
            "paragraphs.\n\n"
            f"Title: {title}\n"
            f"Body: {text}"
        )
        async with self.semaphore:
            return await asyncio.to_thread(self._call_llm_sync, prompt)

    async def clean_one(
        self, article: Article
    ) -> Optional[Tuple[Article, str]]:
        if not article.content or not article.title:
            return None

        try:
            pre_processed = remove_formatting_marks(article.content)
            rewritten = await self.clean_with_llm_removal_only(
                pre_processed, article.title
            )
            if rewritten and rewritten != article.content:
                return article, rewritten
            return None
        except Exception as e:
            logger.error(f"Failed to clean article '{article.title}': {e}")
            return None

    async def clean_articles_since_date(
        self, session: AsyncSession, since_date: date
    ) -> int:
        stmt = select(Article).where(
            Article.content.isnot(None), Article.published_at > since_date
        )
        result = await session.execute(stmt)
        articles = result.scalars().all()

        logger.info(
            f"Found {len(articles)} articles to clean since {since_date}."
        )
        if not articles:
            return 0

        cleaned_results = await asyncio.gather(
            *[self.clean_one(article) for article in articles]
        )

        cleaned_articles = [r for r in cleaned_results if r]

        updated = 0
        for article, new_content in cleaned_articles:
            article.content = new_content
            await ArticleRepository.update_article(article)
            updated += 1

        return updated

    async def clean_articles_after(self, since_date: Optional[date] = None):
        if since_date is None:
            since_date = date.today()
        async with async_session() as session:
            count = await self.clean_articles_since_date(session, since_date)
            logger.info(f"{count} articles cleaned since {since_date}.")


if __name__ == "__main__":
    asyncio.run(ArticleCleaner().clean_articles_after(date(2025, 6, 10)))
