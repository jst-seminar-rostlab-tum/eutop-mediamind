import uuid
from datetime import datetime

from sqlmodel import SQLModel, Field


class SearchProfile(SQLModel):
    __tablename__ = "search_profiles"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    is_public: bool = Field(default=False)
    organization:
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: uuid.UUID = Field(foreign_key="users.id")
