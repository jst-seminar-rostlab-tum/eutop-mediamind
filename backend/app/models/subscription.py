# models/subscription.py

import uuid
from pydantic import AnyUrl
from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship
from .timestamp import TimestampMixin

class Subscription(TimestampMixin, table=True):
    __tablename__ = "subscriptions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    domain: AnyUrl
    vault_path: str = Field(max_length=255)
    config: dict = Field(sa_column=Column(JSON), default_factory=dict)
    scraper_type: str = Field(max_length=255)

    organizations_link = Relationship(back_populates="subscription")
    organizations = Relationship(
        back_populates="subscriptions",
        link_model="OrganizationSubscription",
        sa_relationship_kwargs={"viewonly": True},
    )
