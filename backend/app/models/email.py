import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict

from sqlmodel import JSON, Column, Field, SQLModel
from sqlalchemy import TIMESTAMP, func


class EmailState(Enum):
    PENDING = "pending"
    SENT = "sent"
    RETRY = "retrying"
    FAILED = "failed"


class Email(SQLModel, table=True):
    __tablename__ = "emails"

    # Attributes
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    sender: str = Field(max_length=255, nullable=False)
    recipient: str = Field(max_length=255, nullable=False)
    subject: str = Field(max_length=255, nullable=False)
    content: str = Field(nullable=False)
    content_type: str = Field(default="text/plain", nullable=False)
    attempts: int = Field(default=0, nullable=False)
    attachment: str | None = Field(default=None)
    attachment_name: str | None = Field(default=None)
    attempts: int = Field(default=0, nullable=False)
    state: EmailState = Field(default=EmailState.PENDING, nullable=False)
    errors: Dict[str, str] | None = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    created_at: datetime = Field(sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now()))
    update_at: datetime = Field(sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now()))

    def add_error(self, error: str):
        """
        Add an error message to the email's errors dictionary.
        :param error: The error message to add.
        """
        if self.errors is None:
            self.errors = {}
        self.errors[str(datetime.now(timezone.utc))] = error
