import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List

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

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    subject: str = Field(max_length=500, nullable=False)
    user_email: str = Field(max_length=255, nullable=False, index=True)
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            default=datetime.now(timezone.utc),
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            default=datetime.now(timezone.utc),
            onupdate=func.now(),
        )
    )
    messages: List["ChatMessage"] = Relationship(back_populates="conversation")
