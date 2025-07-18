import uuid
from typing import TYPE_CHECKING, List

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from app.models.associations import OrganizationSubscriptionLink

if TYPE_CHECKING:
    from app.models.search_profile import SearchProfile
    from app.models.subscription import Subscription
    from app.models.user import User


# Database model for organizations
class Organization(SQLModel, table=True):
    __tablename__ = "organizations"
    # Attributes
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, unique=True, index=True)
    email: EmailStr = Field(max_length=255, index=True, nullable=True)
    vault_path: str | None = Field(default=None, max_length=255)
    # Relationships
    users: List["User"] = Relationship(back_populates="organization")
    search_profiles: List["SearchProfile"] = Relationship(
        back_populates="organization",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    subscriptions: List["Subscription"] = Relationship(
        back_populates="organizations", link_model=OrganizationSubscriptionLink
    )
    pdf_as_link: bool = Field(default=True)


# Pydantic schemas for API
class OrganizationBase(SQLModel):
    name: str = Field(max_length=255)
    email: EmailStr = Field(max_length=255)
