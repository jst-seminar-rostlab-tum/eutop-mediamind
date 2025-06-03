from typing import Sequence, Optional
from uuid import UUID

from sqlmodel import Session, select

from app.models.article import Article
from app.core.db import engine


class ArticleRepository:
    @staticmethod
    def get_article_by_id(article_id: UUID) -> Optional[Article]:
        """
        Retrieve a single Article by its UUID.
        Returns None if no article is found.
        """
        with Session(engine) as session:
            statement = select(Article).where(Article.id == article_id)
            result = session.exec(statement)
            return result.first()

    @staticmethod
    def update_article(article: Article) -> Optional[Article]:
        """
        Update an existing Article in the database.
        Returns the updated Article, or None if it does not exist.
        """
        with Session(engine) as session:
            existing = session.get(Article, article.id)
            if not existing:
                return None
            for attr, value in vars(article).items():
                if attr.startswith("_"):
                    continue
                setattr(existing, attr, value)
            session.add(existing)
            session.commit()
            session.refresh(existing)
            return existing

    @staticmethod
    def create_article(article: Article) -> Article:
        """
        Add a new Article to the database.
        """
        with Session(engine) as session:
            session.add(article)
            session.commit()
            session.refresh(article)
            return article

    @staticmethod
    @staticmethod
    def list_articles(limit: int = 100, offset: int = 0, set_of: int = 0) -> Sequence[Article]:
        """
        List articles with optional pagination and batch processing.
        """
        with Session(engine) as session:
            statement = select(Article).limit(limit).offset(offset + (set_of * limit))
            result = session.exec(statement)
            return result.all()
