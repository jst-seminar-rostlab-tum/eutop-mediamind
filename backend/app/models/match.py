import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.article import Article
    from app.models.search_profile import SearchProfile


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
    sorting_order: int = Field(default=0)
    comment: str | None = Field(default=None, max_length=255)

    # Relationships
    article: "Article" = Relationship(back_populates="matches")
    search_profile: "SearchProfile" = Relationship(back_populates="matches")
