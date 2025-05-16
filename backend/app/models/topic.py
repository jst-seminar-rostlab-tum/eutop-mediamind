import uuid

from sqlmodel import SQLModel, Field


class Topic(SQLModel):
    __tablename__ = "topics"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    description: str = Field(max_length=255)
