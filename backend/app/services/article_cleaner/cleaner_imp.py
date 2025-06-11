import asyncio
from datetime import date
import re
from asyncio import Semaphore

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from openai import OpenAI

from app.core.config import configs
from app.models.article import Article, ArticleStatus
from app.repositories.subscription_repository import SubscriptionRepository

# DB setup
engine = create_async_engine(str(configs.SQLALCHEMY_DATABASE_URI), echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class ArticleCleaner:
    def __init__(self, max_concurrency: int = 5):
        self.client = OpenAI(api_key=configs.OPENAI_API_KEY)
        self.semaphore = Semaphore(max_concurrency)

    def remove_formatting_marks(self, text: str) -> str:
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # remove bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # remove italics
        text = re.sub(r'#+\s+', '', text)             # remove markdown headers
        text = re.sub(r'^-{3,}$', '', text, flags=re.MULTILINE)  # remove horizontal lines
        text = re.sub(r'\[.*?\]\(.*?\)', '', text)    # remove markdown links
        text = re.sub(r'\s{2,}', ' ', text)           # remove extra spaces
        return text.strip()
    
    async def rewrite_with_llm(self, text: str) -> str:
        prompt = (
            "The following news article contains formatting artifacts such as markdown symbols (**bold**, *italic*, footnotes), "
            "author lines, inline references, and other structural noise. Please rewrite the text into a clean, well-structured, "
            "readable article. Keep the factual content, but remove all formatting marks, links, metadata, and stylistic clutter. "
            "The result should look like a professional news article with proper paragraphing and flow.\n\n"
            f"{text}"
        )
        async with self.semaphore:
            return await asyncio.to_thread(self._call_openai_sync, prompt)

    def _call_openai_sync(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    

    async def clean_one(self, article: Article) -> tuple[Article, str] | None:
        try:
            pre_processed = self.remove_formatting_marks(article.content)
            rewritten = await self.rewrite_with_llm(pre_processed)
            if rewritten and rewritten != article.content:
                return article, rewritten
            return None
        except Exception as e:
            print(f"[ERROR] Failed to clean article '{article.title}': {e}")
            return None
        

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
        # 并发处理所有文章
        cleaned_results = await asyncio.gather(
            *[self.clean_one(article) for article in articles]
        )

        # 过滤掉未改变或失败的
        cleaned_articles = [r for r in cleaned_results if r]

        # 逐篇写入数据库
        updated = 0
        for article, new_content in cleaned_articles:
            article.content = new_content
            article.status = ArticleStatus.CLEANED
            await SubscriptionRepository.update_article(session, article)
            updated += 1

        return updated

    async def run(self):
        async with async_session() as session:
            count = await self.clean_articles_after_date(session)
            print(f"{count} articles cleaned.")


if __name__ == "__main__":
    asyncio.run(ArticleCleaner().run())
