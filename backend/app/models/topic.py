# models/topic.py

import uuid
from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship, SQLModel

from app.models.associations import TopicKeywordLink

if TYPE_CHECKING:
    from app.models.keyword import Keyword
    from app.models.search_profile import SearchProfile
    from app.models.match import Match


class Topic(SQLModel, table=True):
    __tablename__ = "topics"
    # Attributes
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=255)
    search_profile_id: uuid.UUID = Field(
        foreign_key="search_profiles.id", nullable=False, index=True
    )

    # Relationships
    search_profile: "SearchProfile" = Relationship(back_populates="topics")
    keywords: List["Keyword"] = Relationship(
        back_populates="topics",
        link_model=TopicKeywordLink,
    )

    matches: List["Match"] = Relationship(back_populates="topic")

