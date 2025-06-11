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
    def __init__(self, max_concurrency: int = 100):
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
    
    async def rewrite_with_llm(self, text, title: str) -> str:
        prompt = (
            "The following news article contains unwanted formatting artifacts such as markdown symbols (**bold**, *italic*, footnotes), "
            "author lines, inline references, and other structural noise.\n"
            "Your task is to remove noise, for example:\n"
            "Formatting marks, links, metadata, stylistic clutter and duplicated content.\n"
            "Remove duplicate title inside the body. If the first sentence is semantically very similar to the title, even with minor rewordings, remove it.\n"
            "Do not paraphrase or add any new content. Only remove noise.\n"
            "Don't change the language of the article, it should remain the same as the original.\n"
            "Return only the cleaned body text, properly structured in paragraphs.\n\n"
            f"Title: {title}\n"
            f"Body: {text}"
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
            rewritten = await self.rewrite_with_llm(pre_processed, article.title)
            if rewritten and rewritten != article.content:
                return article, rewritten
            return None
        except Exception as e:
            print(f"[ERROR] Failed to clean article '{article.title}': {e}")
            return None
        

    async def clean_articles_after_date(
        self,
        session: AsyncSession,
        since_date: date = date(2025, 6, 5)
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
       
        cleaned_results = await asyncio.gather(
            *[self.clean_one(article) for article in articles]
        )

        
        cleaned_articles = [r for r in cleaned_results if r]

        
        updated = 0
        for article, new_content in cleaned_articles:
            article.content = new_content
            # article.status = ArticleStatus.CLEANED
            await SubscriptionRepository.update_article(session, article)
            updated += 1

        return updated

    async def run(self):
        async with async_session() as session:
            count = await self.clean_articles_after_date(session)
            print(f"{count} articles cleaned.")


if __name__ == "__main__":
    asyncio.run(ArticleCleaner().run())
