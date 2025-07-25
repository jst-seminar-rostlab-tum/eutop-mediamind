from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import TIMESTAMP, Column, Text
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .email_conversation import EmailConversation


class MessageRole(Enum):
    USER = "user"  # User messages
    ASSISTANT = "assistant"  # AI messages


class ChatMessage(SQLModel, table=True):
    """
    Represents individual messages in an email conversation.
    Stores both user messages and AI responses.
    """

    __tablename__ = "chat_messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email_conversation_id: UUID = Field(foreign_key="email_conversations.id")
    role: MessageRole
    content: str = Field(
        sa_column=Column(Text, nullable=False),
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
        ),
    )
    conversation: "EmailConversation" = Relationship(back_populates="messages")
