# models/article.py

import uuid
from datetime import date
from typing import List, Optional
from pydantic import AnyUrl
from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship
from .timestamp import TimestampMixin

class Article(TimestampMixin, table=True):
    __tablename__ = "articles"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    url: AnyUrl
    title: str = Field(max_length=255, index=True)
    author: str = Field(max_length=255)
    content: str
    published: date
    lang: str = Field(max_length=10)
    category: str = Field(max_length=50)
    summary: str = Field(max_length=255)
    vector_embedding: Optional[List[float]] = Field(
        default=None, sa_column=Column(JSON)
    )

    keywords_link = Relationship(back_populates="article")
    keywords = Relationship(
        back_populates="articles",
        link_model="ArticleKeyword",
        sa_relationship_kwargs={"viewonly": True},
    )
    matches = Relationship(back_populates="article")
