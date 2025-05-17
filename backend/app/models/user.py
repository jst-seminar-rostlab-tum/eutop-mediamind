# models/user.py

import uuid
from pydantic import EmailStr
from sqlmodel import Field, Relationship
from sqlalchemy import UniqueConstraint
from .timestamp import TimestampMixin

class User(TimestampMixin, table=True):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_user_email"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_admin: bool = Field(default=False)
    organization_id: uuid.UUID = Field(foreign_key="organizations.id")

    organization = Relationship(back_populates="users")
    search_profiles = Relationship(back_populates="created_by_user")
    matches = Relationship(back_populates="comment_by")
