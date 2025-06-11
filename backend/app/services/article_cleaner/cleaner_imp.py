import asyncio
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from openai import OpenAI

from app.core.config import configs
from app.models.article import Article
from app.repositories.subscription_repository import SubscriptionRepository

# DB setup
engine = create_async_engine(str(configs.SQLALCHEMY_DATABASE_URI), echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class ArticleCleaner:
    def __init__(self):
        self.client = OpenAI(api_key=configs.OPENAI_API_KEY)

    def rewrite_with_llm(self, text: str) -> str:
        prompt = (
            "Dies ist ein beschädigter Nachrichtentext. Bitte rekonstruiere ihn als vollständigen, "
            "sauberen Artikel, und entferne unnötige Informationen:\n\n"
            f"{text}"
        )
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()

    async def clean_articles_after_date(
        self,
        session: AsyncSession,
        since_date: date = date(2025, 5, 20)
    ) -> int:
        stmt = select(Article).where(
            Article.content.isnot(None),
            Article.published_at > since_date
        )
        result = await session.execute(stmt)
        articles = result.scalars().all()

        print(f"Found {len(articles)} articles to clean since {since_date}.")
        if not articles:
            return 0

        cleaned_count = 0
        for article in articles:
            rewritten = self.rewrite_with_llm(article.content)
            article.content = rewritten
            await SubscriptionRepository.update_article(session, article)
            cleaned_count += 1

        return cleaned_count

    async def run(self):
        async with async_session() as session:
            count = await self.clean_articles_after_date(session)
            print(f"{count} articles cleaned.")


if __name__ == "__main__":
    asyncio.run(ArticleCleaner().run())
