import uuid

from sqlmodel import SQLModel, Field


class Match(SQLModel):
    __tablename__ = "matches"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    sorting_order: int = Field(default=0)
    comment: str = Field(max_length=255)
    comment_by:
    search_profile:
    article:

