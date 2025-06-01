import uuid
from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship, SQLModel

from app.models.associations import (
    OrganizationSubscriptionLink,
    SearchProfileSubscriptionLink,
)

if TYPE_CHECKING:
    from app.models.article import Article
    from app.models.organization import Organization
    from app.models.search_profile import SearchProfile


class Subscription(SQLModel, table=True):
    __tablename__ = "subscriptions"
    # Attributes
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, unique=True)
    domain: str = Field(max_length=255)
    paywall: bool = Field(default=False)
    login_works: bool = Field(default=False)
    newsapi_id: str = Field(default=None, max_length=255, nullable=True)
    vault_path: str = Field(max_length=255, nullable=True)
    config: str = Field(max_length=255, nullable=True)
    scraper_type: str = Field(max_length=255, nullable=True)

    # Relationships
    organizations: List["Organization"] = Relationship(
        back_populates="subscriptions",
        link_model=OrganizationSubscriptionLink,
    )
    articles: List["Article"] = Relationship(
        back_populates="subscription",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    search_profiles: List["SearchProfile"] = Relationship(
        back_populates="subscriptions",
        link_model=SearchProfileSubscriptionLink,
    )
