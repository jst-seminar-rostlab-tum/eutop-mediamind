import uuid
from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship, SQLModel

from app.models.associations import ArticleKeywordLink, TopicKeywordLink

if TYPE_CHECKING:
    from app.models.article import Article
    from app.models.topic import Topic


class Keyword(SQLModel, table=True):
    __tablename__ = "keywords"
    # Attributes
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)

    # Relationships
    topics: List["Topic"] = Relationship(
        back_populates="keywords", link_model=TopicKeywordLink
    )
    articles: List["Article"] = Relationship(
        back_populates="keywords", link_model=ArticleKeywordLink
    )
