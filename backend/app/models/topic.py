# models/topic.py

import uuid
from sqlmodel import Field, Relationship
from .timestamp import TimestampMixin

class Topic(TimestampMixin, table=True):
    __tablename__ = "topics"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    description: str = Field(max_length=255)
    search_profile_id: uuid.UUID = Field(foreign_key="search_profiles.id")

    search_profile = Relationship(back_populates="topics")
    topics_link = Relationship(back_populates="topic")
    keywords = Relationship(
        back_populates="topics",
        link_model="TopicKeyword",
        sa_relationship_kwargs={"viewonly": True},
    )
