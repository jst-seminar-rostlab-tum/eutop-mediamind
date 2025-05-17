# models/keyword.py

import uuid
from sqlmodel import Field, Relationship
from sqlalchemy import UniqueConstraint
from .timestamp import TimestampMixin

class Keyword(TimestampMixin, table=True):
    __tablename__ = "keywords"
    __table_args__ = (UniqueConstraint("term", name="uq_keyword_term"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    term: str = Field(max_length=255, index=True)

    articles_link = Relationship(back_populates="keyword")
    articles = Relationship(
        back_populates="keywords",
        link_model="ArticleKeyword",
        sa_relationship_kwargs={"viewonly": True},
    )
    topics_link = Relationship(back_populates="keyword")
    topics = Relationship(
        back_populates="keywords",
        link_model="TopicKeyword",
        sa_relationship_kwargs={"viewonly": True},
    )
