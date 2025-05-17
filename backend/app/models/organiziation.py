# models/organization.py

import uuid
from pydantic import EmailStr
from sqlalchemy import Column, JSON, UniqueConstraint
from sqlmodel import Field, Relationship
from .timestamp import TimestampMixin

class Organization(TimestampMixin, table=True):
    __tablename__ = "organizations"
    __table_args__ = (UniqueConstraint("email", name="uq_org_email"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    email: EmailStr = Field(max_length=255, index=True)
    vault_path: str = Field(max_length=255)

    users = Relationship(back_populates="organization")
    subscriptions_link = Relationship(back_populates="organization")
    subscriptions = Relationship(
        back_populates="organizations",
        link_model="OrganizationSubscription",
        sa_relationship_kwargs={"viewonly": True},
    )
    search_profiles = Relationship(back_populates="organization")
