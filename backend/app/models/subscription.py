import uuid
from typing import TYPE_CHECKING, Any, List, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Boolean, Field, Relationship, SQLModel

from app.models.associations import (
    OrganizationSubscriptionLink,
    SearchProfileSubscriptionLink,
)

if TYPE_CHECKING:
    from app.models.article import Article
    from app.models.organization import Organization
    from app.models.search_profile import SearchProfile

from cryptography.fernet import Fernet

from app.core.config import configs

fernet = Fernet(configs.FERNET_KEY)


class Subscription(SQLModel, table=True):
    __tablename__ = "subscriptions"
    # Attributes
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, unique=True)
    domain: str = Field(max_length=255)
    paywall: bool = Field(default=False)

    # Attributes for Webcrawling/Scraping
    is_active: bool = Field(
        default=False,
        sa_column=Column(Boolean, default=False, nullable=False,
                         comment="Indicates if this is included in the "
                         "webcrawling pipeline")
    )
    crawlers: Optional[dict[str, dict[str, Any]]] = Field(
        sa_column=Column(JSON, nullable=True, default=None,
                         comment="List of Crawlers used"
                         "for this subscription. Contains the Class and the "
                         "config to initializer the Crawler")
    )
    login_config: Optional[dict] = Field(
        sa_column=Column(JSON, default=None, nullable=True,
                         comment="Contains "
                         "the xpath for the scraping of "
                         "paywalled newspapers"))

    encrypted_secrets: Optional[bytes] = Field(
        default=None, sa_column_kwargs={"nullable": True}
    )

    scrapers: Optional[dict[str, dict[str, Any]]] = Field(
        sa_column=Column(JSON, nullable=True, default=None, comment="List of "
                         "Scrapers used "
                         "for this subscription. Contains the Class and the "
                         "config to initialize the Scraper"),
    )

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

    @property
    def secrets(self) -> Optional[str]:
        if self.encrypted_secrets:
            return fernet.decrypt(self.encrypted_secrets).decode()
        return None

    @secrets.setter
    def secrets(self, value: str):
        self.encrypted_secrets = fernet.encrypt(value.encode())
