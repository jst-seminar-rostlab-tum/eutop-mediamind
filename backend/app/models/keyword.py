import uuid
from sqlmodel import Field, SQLModel, Relationship
from typing import List
from typing import TYPE_CHECKING
from app.models.associations import TopicKeywordLink
from app.models.associations import ArticleKeywordLink


if TYPE_CHECKING:
    from app.models.topic import Topic
    from app.models.article import Article


class Keyword(SQLModel, table=True):
    __tablename__ = "keywords"
    # Attributes
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)

    # Relationships
    topics: List["Topic"] = Relationship(
        back_populates="keywords",
        link_model=TopicKeywordLink
    )
    articles: List["Article"] = Relationship(
        back_populates="keywords",
        link_model=ArticleKeywordLink
    )
