import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, Column, Text
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.article import Article
    from app.models.search_profile import SearchProfile
    from app.models.topic import Topic


class Match(SQLModel, table=True):
    __tablename__ = "matches"
    # Attributes
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    article_id: uuid.UUID = Field(
        foreign_key="articles.id", nullable=False, index=True
    )
    search_profile_id: uuid.UUID = Field(
        foreign_key="search_profiles.id", nullable=False, index=True
    )
    topic_id: uuid.UUID | None = Field(
        default=None, foreign_key="topics.id", index=True
    )

    sorting_order: int = Field(default=0)
    comment: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )
    score: float = Field(default=0.0)

    matched_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            default=datetime.now(timezone.utc),
        )
    )

    # Relationships
    article: "Article" = Relationship(back_populates="matches")
    search_profile: "SearchProfile" = Relationship(back_populates="matches")
    topic: "Topic" = Relationship(back_populates="matches")
