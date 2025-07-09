import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import ARRAY, CheckConstraint, Column, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import Field, Relationship, SQLModel

from .associations import SearchProfileSubscriptionLink, UserSearchProfileLink
from .organization import Organization

if TYPE_CHECKING:
    from .match import Match
    from .report import Report
    from .subscription import Subscription
    from .topic import Topic
    from .user import User


class SearchProfile(SQLModel, table=True):
    __tablename__ = "search_profiles"
    # Attributes
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    is_public: bool = Field(default=False)
    created_by_id: uuid.UUID = Field(foreign_key="users.id")
    owner_id: uuid.UUID = Field(default=None, foreign_key="users.id")
    organization_id: uuid.UUID = Field(foreign_key="organizations.id")
    organization: Organization = Relationship(back_populates="search_profiles")
    organization_emails: List[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(String), server_default="{}")
    )
    profile_emails: List[str] = Field(sa_column=Column(ARRAY(String)))
    can_read_user_ids: List[uuid.UUID] = Field(
        default_factory=list,
        sa_column=Column(
            ARRAY(PG_UUID(as_uuid=True)),  # use the PG dialect type
            server_default="{}",  # defaults to empty array
        ),
    )
    can_edit_user_ids: List[uuid.UUID] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(PG_UUID(as_uuid=True)), server_default="{}"),
    )
    # Language with default English
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

    # Relationships
    users: List["User"] = Relationship(
        back_populates="search_profiles", link_model=UserSearchProfileLink
    )

    topics: list["Topic"] = Relationship(
        back_populates="search_profile",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    matches: list["Match"] = Relationship(
        back_populates="search_profile",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    subscriptions: list["Subscription"] = Relationship(
        back_populates="search_profiles",
        link_model=SearchProfileSubscriptionLink,
    )
    reports: List["Report"] = Relationship(
        back_populates="search_profile",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


# Pydantic schemas for API
class SearchProfileBase(SQLModel):
    name: str = Field(max_length=255)
    organization_id: uuid.UUID
    language: str = Field(default="en")


class SearchProfileCreate(SearchProfileBase):
    pass


class SearchProfileUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    language: str | None = Field(default="en")


class SearchProfileRead(SearchProfileBase):
    id: uuid.UUID


class SearchProfilesRead(SQLModel):
    data: list[SearchProfileRead]
    count: int
