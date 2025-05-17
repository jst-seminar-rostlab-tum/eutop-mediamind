import uuid
from typing import List
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
from app.models.associations import OrganizationSubscriptionLink
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.search_profile import SearchProfile
    from app.models.subscription import Subscription

# Database model for organizations
class Organization(SQLModel, table=True):
    __tablename__ = "organizations"
    # Attributes
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, unique=True, index=True)
    email: EmailStr = Field(max_length=255, index=True)
    vault_path: str | None = Field(default=None, max_length=255)
    # Relationships
    users: List["User"] = Relationship(back_populates="organization")
    search_profiles: List["SearchProfile"] = Relationship(
        back_populates="organization",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    subscriptions: List["Subscription"] = Relationship(
        back_populates="organizations",
        link_model=OrganizationSubscriptionLink
    )
    

# Pydantic schemas for API
class OrganizationBase(SQLModel):
    name: str = Field(max_length=255)
    email: EmailStr = Field(max_length=255)

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationRead(OrganizationBase):
    id: uuid.UUID

class OrganizationUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)

class OrganizationsRead(SQLModel):
    data: list[OrganizationRead]
    count: int
