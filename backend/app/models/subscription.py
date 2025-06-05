import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

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
    name: str = Field(max_length=255)
    domain: str = Field(max_length=255)
    config: str = Field(max_length=255)
    scraper_type: str = Field(max_length=255)
    encrypted_secrets: Optional[bytes] = Field(
        default=None, sa_column_kwargs={"nullable": True}
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
