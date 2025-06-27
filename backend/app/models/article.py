import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column, Text
from sqlmodel import JSON, Field, Relationship, SQLModel

from app.models.associations import (
    ArticleKeywordLink,
)

if TYPE_CHECKING:
    from app.models.entity import ArticleEntity
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
    image_url: Optional[str] = Field(
        default=None,
        sa_column=Column(
            Text, nullable=True, comment="URL of " "the article's image"
        ),
    )
    authors: List[str] = Field(
        sa_column=Column(
            JSON,
            nullable=True,
            default=None,
            comment="List of authors for the article",
        ),
    )
    published_at: datetime = Field()
    language: str = Field(max_length=255, nullable=True)
    categories: List[str] = Field(
        sa_column=Column(
            JSON,
            nullable=True,
            default=None,
            comment="List of categories for the article",
        ),
    )
    summary: str | None = Field(default=None, sa_column=Column(Text))
    status: ArticleStatus = Field(default=ArticleStatus.NEW, nullable=False)
    relevance: int = Field(default=0, nullable=False)

    title_en: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    title_de: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    content_en: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    content_de: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    summary_en: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    summary_de: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )

    crawled_at: datetime = Field(default_factory=datetime.now)
    scraped_at: Optional[datetime] = Field(default=None, nullable=True)

    # Contains a note or error message related to the article
    note: Optional[str] = Field(default=None, nullable=True)

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
    entities: List["ArticleEntity"] = Relationship(back_populates="article")
