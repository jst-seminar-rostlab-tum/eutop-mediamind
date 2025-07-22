from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import TIMESTAMP, Column, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .chat_message import ChatMessage


class EmailConversation(SQLModel, table=True):
    """
    Represents an email conversation thread for the chatbot.
    Groups related emails and chat messages together.
    """

    __tablename__ = "email_conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    subject: str = Field(max_length=500, nullable=False)
    user_email: str = Field(max_length=255, nullable=False, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
        ),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            onupdate=func.now(),
        ),
    )
    report_id: Optional[UUID] = Field(foreign_key="reports.id", nullable=True)
    messages: List["ChatMessage"] = Relationship(back_populates="conversation")
