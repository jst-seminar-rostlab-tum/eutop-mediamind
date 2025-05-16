import uuid

from sqlmodel import SQLModel, Field


class Organization(SQLModel):
    __tablename__ = "organizations"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    email: str = Field(max_length=255)
    vault_path: str = Field(max_length=255)
