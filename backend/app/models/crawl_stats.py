import uuid
from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.subscription import Subscription


class CrawlStats(SQLModel, table=True):
    __tablename__ = "crawl_stats"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Foreign Key to Subscription
    subscription_id: uuid.UUID = Field(
        foreign_key="subscriptions.id", nullable=False, index=True
    )
    subscription: Optional["Subscription"] = Relationship(
        back_populates="crawl_stats"
    )

    total_successful: int = Field(default=0, nullable=False)
    total_attempted: int = Field(default=0, nullable=False)

    crawl_date: date = Field(default_factory=date.today, nullable=False)

    notes: Optional[str] = Field(default=None, nullable=True)
