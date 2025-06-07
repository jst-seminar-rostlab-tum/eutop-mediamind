import uuid
from typing import TYPE_CHECKING, List

from pydantic import BaseModel, EmailStr
from sqlmodel import Field, Relationship, SQLModel

from app.models.associations import UserSearchProfileLink

from .organization import Organization

if TYPE_CHECKING:

    from app.models.search_profile import SearchProfile


class UserCreate(BaseModel):
    clerk_id: str
    email: str
    first_name: str
    last_name: str
    is_superuser: bool = False
    organization_id: uuid.UUID | None = None


# Shared properties
class UserBase(SQLModel):
    clerk_id: str = Field(max_length=255, index=True)
    email: EmailStr = Field(index=True, max_length=255)
    first_name: str = Field(max_length=255)
    last_name: str = Field(max_length=255)
    is_superuser: bool = Field(default=False)
    organization_id: uuid.UUID | None = Field(
        default=None, foreign_key="organizations.id"
    )


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


# Database model, table inferred from class name
class User(UserBase, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    organization: Organization = Relationship(back_populates="users")
    search_profiles: List["SearchProfile"] = Relationship(
        back_populates="users",
        link_model=UserSearchProfileLink,
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int
