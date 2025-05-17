# models/match.py

import uuid
from sqlmodel import Field, Relationship
from .timestamp import TimestampMixin

class Match(TimestampMixin, table=True):
    __tablename__ = "matches"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    sorting_order: int = Field(default=0)
    comment: str = Field(max_length=255)
    comment_by_id: uuid.UUID = Field(foreign_key="users.id")
    search_profile_id: uuid.UUID = Field(foreign_key="search_profiles.id")
    article_id: uuid.UUID = Field(foreign_key="articles.id")

    comment_by = Relationship(back_populates="matches")
    search_profile = Relationship(back_populates="matches")
    article = Relationship(back_populates="matches")
