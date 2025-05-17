# models/search_profile.py

import uuid
from pydantic import EmailStr
from sqlmodel import Field, Relationship
from sqlalchemy import UniqueConstraint
from .timestamp import TimestampMixin

class SearchProfile(TimestampMixin, table=True):
    __tablename__ = "search_profiles"
    __table_args__ = (UniqueConstraint("name", "organization_id", name="uq_sp_name_org"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    customer_name: str = Field(max_length=255)
    customer_email: EmailStr = Field(max_length=255)
    is_public: bool = Field(default=False)
    organization_id: uuid.UUID = Field(foreign_key="organizations.id")
    created_by_id: uuid.UUID = Field(foreign_key="users.id")

    organization = Relationship(back_populates="search_profiles")
    created_by_user = Relationship(back_populates="search_profiles")
    topics = Relationship(back_populates="search_profile")
    matches = Relationship(back_populates="search_profile")
