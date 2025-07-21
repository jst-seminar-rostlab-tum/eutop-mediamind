import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Dict, Optional

from sqlalchemy import TIMESTAMP
from sqlmodel import JSON, Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .report import Report


class EmailState(Enum):
    PENDING = "pending"
    SENT = "sent"
    RETRY = "retrying"
    FAILED = "failed"


class Email(SQLModel, table=True):
    __tablename__ = "emails"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    sender: str = Field(max_length=255, nullable=False)
    recipient: str = Field(max_length=255, nullable=False)
    subject: str = Field(max_length=255, nullable=False)
    content: str = Field(nullable=False)
    content_type: str = Field(default="text/plain", nullable=False)
    attempts: int = Field(default=0, nullable=False)
    state: EmailState = Field(default=EmailState.PENDING, nullable=False)
    errors: Dict[str, str] | None = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
        ),
    )
    update_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
        ),
    )
    report_id: Optional[uuid.UUID] = Field(
        foreign_key="reports.id", nullable=True
    )
    report: Optional["Report"] = Relationship(back_populates="emails")

    def add_error(self, error: str):
        """
        Add an error message to the email's errors dictionary.
        :param error: The error message to add.
        """
        if self.errors is None:
            self.errors = {}
        self.errors[str(datetime.now(timezone.utc))] = error
