import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

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

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email_conversation_id: uuid.UUID = Field(
        foreign_key="email_conversations.id"
    )
    role: MessageRole
    content: str = Field(
        sa_column=Column(Text, nullable=False),
    )
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            default=datetime.now(timezone.utc),
        )
    )
    conversation: "EmailConversation" = Relationship(back_populates="messages")
