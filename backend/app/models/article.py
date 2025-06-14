import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column, Text
from sqlmodel import Field, Relationship, SQLModel

from app.models.associations import (
    ArticleKeywordLink,
)

if TYPE_CHECKING:
    from app.models.keyword import Keyword
    from app.models.match import Match
    from app.models.subscription import Subscription


class ArticleStatus(str, Enum):
    NEW = "new"
    SCRAPED = "scraped"
    ERROR = "error"


class Article(SQLModel, table=True):
    __tablename__ = "articles"

    # Attributes
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    content: str = Field(nullable=True)
    url: str = Field(max_length=255, unique=True)
    author: str = Field(max_length=255, nullable=True)
    published_at: datetime = Field()
    language: str = Field(max_length=255, nullable=True)
    category: str = Field(max_length=255, nullable=True)
    summary: str | None = Field(default=None, sa_column=Column(Text))
    status: ArticleStatus = Field(default=ArticleStatus.NEW, nullable=False)

    crawled_at: datetime = Field(default_factory=datetime.now)
    scraped_at: Optional[datetime] = Field(default=None, nullable=True)

    # vector_embedding
    subscription_id: uuid.UUID = Field(
        foreign_key="subscriptions.id", nullable=False, index=True
    )

    # Relationships
    subscription: "Subscription" = Relationship(back_populates="articles")
    keywords: List["Keyword"] = Relationship(
        back_populates="articles",
        link_model=ArticleKeywordLink,
    )
    matches: List["Match"] = Relationship(back_populates="article")
