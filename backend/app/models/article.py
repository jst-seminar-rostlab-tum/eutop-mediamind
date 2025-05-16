from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel
import uuid

class Article(SQLModel):
    __tablename__ = "articles"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    author: str = Field(max_length=255)
    content: str = Field()
    published: datetime = Field()
    language: str = Field(max_length=10)
    category: str = Field(max_length=50)
    summary: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.now)