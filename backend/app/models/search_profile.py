from sqlmodel import SQLModel, Field, Relationship
import uuid
from .organization import Organization
from typing import TYPE_CHECKING, List
from .associations import SearchProfileSubscriptionLink
from .associations import UserSearchProfileLink
if TYPE_CHECKING:
    from .topic import Topic
    from .match import Match
    from .subscription import Subscription
    from .user import User


class SearchProfile(SQLModel, table=True):
    __tablename__ = "search_profiles"
    # Attributes
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    is_public: bool = Field(default=False)
    created_by_id: uuid.UUID = Field(foreign_key="users.id")
    organization_id: uuid.UUID = Field(foreign_key="organizations.id")
    organization: Organization = Relationship(back_populates="search_profiles")

    # Relationships
    users: List["User"] = Relationship(
        back_populates="search_profiles",
        link_model=UserSearchProfileLink
    )
    
    topics: list["Topic"] = Relationship(
        back_populates="search_profile",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    matches: list["Match"] = Relationship(
        back_populates="search_profile",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    subscriptions: list["Subscription"] = Relationship(
        back_populates="search_profiles",
        link_model=SearchProfileSubscriptionLink
    )


# Pydantic schemas for API
class SearchProfileBase(SQLModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=255)
    organization_id: uuid.UUID

class SearchProfileCreate(SearchProfileBase):
    pass

class SearchProfileUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=255)

class SearchProfileRead(SearchProfileBase):
    id: uuid.UUID

class SearchProfilesRead(SQLModel):
    data: list[SearchProfileRead]
    count: int


