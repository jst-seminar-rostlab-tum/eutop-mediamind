import uuid
from enum import Enum
from typing import TYPE_CHECKING, List

from pydantic import EmailStr
from sqlalchemy import CheckConstraint, Column
from sqlalchemy import Enum as SqlAlchemyEnum
from sqlalchemy import String
from sqlmodel import Field, Relationship, SQLModel

from app.models.associations import UserSearchProfileLink

from .organization import Organization

if TYPE_CHECKING:
    from app.models.search_profile import SearchProfile


class UserRole(str, Enum):
    maintainer = "maintainer"
    member = "member"


class Gender(str, Enum):
    male = "male"
    female = "female"
    divers = "divers"


# Shared properties
class UserBase(SQLModel):
    clerk_id: str = Field(max_length=255, index=True)
    email: EmailStr = Field(index=True, max_length=255)
    first_name: str = Field(max_length=255)
    last_name: str = Field(max_length=255)
    is_superuser: bool = Field(default=False)
    breaking_news: bool = Field(default=True)
    organization_id: uuid.UUID | None = Field(
        default=None, foreign_key="organizations.id"
    )
    # New language field on the base schema (default=en)
    language: str = Field(
        default="en",
        regex=r"^(en|de)$",
        sa_column=Column(
            String(2),
            CheckConstraint(
                "language IN ('en','de')", name="ck_search_profiles_language"
            ),
            nullable=False,
            server_default="en",
        ),
        description="Language code, must be 'en' or 'de'",
    )
    role: UserRole = Field(
        sa_column=Column(
            SqlAlchemyEnum(UserRole, name="user_role_enum"),
            nullable=False,
            server_default=UserRole.member.value,
        ),
    )
    gender: Gender | None = Field(
        default=Gender.male,
        sa_column=Column(
            SqlAlchemyEnum(Gender, name="gender_enum"),
            nullable=True,
            server_default=Gender.male.value,
        ),
    )


# Database model, table inferred from class name
class User(UserBase, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    organization: Organization = Relationship(back_populates="users")
    search_profiles: List["SearchProfile"] = Relationship(
        back_populates="users",
        link_model=UserSearchProfileLink,
    )
