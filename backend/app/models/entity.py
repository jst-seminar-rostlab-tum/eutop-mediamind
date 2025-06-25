import uuid
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, Text
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.article import Article


class EntityType(str, Enum):
    PERSON = "person"
    INDUSTRY = "industry"
    EVENT = "event"
    ORGANIZATION = "organization"


class ArticleEntity(SQLModel, table=True):
    __tablename__ = "entities"

    # Attributes
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    entity_type: EntityType = Field(sa_column=Column(Text, nullable=False))
    value: str = Field(max_length=255, nullable=False)

    article_id: uuid.UUID = Field(
        foreign_key="articles.id", nullable=False, index=True
    )

    # Relationship
    article: "Article" = Relationship(back_populates="entities")
