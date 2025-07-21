import uuid
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.core.db import async_session
from app.models.chat_message import ChatMessage, MessageRole
from app.models.email_conversation import EmailConversation


class ChatbotRepository:
    @staticmethod
    async def get_conversation_by_email_and_subject(
        user_email: str, subject: str
    ) -> Optional[EmailConversation]:
        """
        Find existing conversation by user email and subject.
        """
        query = (
            select(EmailConversation)
            .options(selectinload(EmailConversation.messages))
            .where(
                EmailConversation.user_email == user_email,
                EmailConversation.subject == subject,
            )
        )
        async with async_session() as session:
            email_conversation = await session.execute(query)
            return email_conversation.scalar_one_or_none()

    @staticmethod
    async def create_conversation(
        user_email: str, subject: str, report_id: uuid.UUID
    ) -> EmailConversation:
        """
        Create a new email conversation.
        """
        new_email_conversation = EmailConversation(
            user_email=user_email,
            subject=subject,
            report_id=report_id,
        )
        async with async_session() as session:
            session.add(new_email_conversation)
            await session.commit()
            await session.refresh(new_email_conversation)
            return new_email_conversation

    @staticmethod
    async def add_message(
        email_conversation_id: uuid.UUID,
        role: MessageRole,
        content: str,
    ) -> ChatMessage:
        """
        Add a message to a conversation.
        """
        message = ChatMessage(
            email_conversation_id=email_conversation_id,
            role=role,
            content=content,
        )
        async with async_session() as session:
            session.add(message)
            await session.commit()
            await session.refresh(message)
            return message

    @staticmethod
    async def get_conversation_history(
        email_conversation_id: uuid.UUID,
    ) -> List[ChatMessage]:
        """
        Get all messages for a conversation ordered by creation time.
        """
        query = (
            select(ChatMessage)
            .where(ChatMessage.email_conversation_id == email_conversation_id)
            .order_by(ChatMessage.created_at)
        )
        async with async_session() as session:
            chat_messages = await session.execute(query)
            return chat_messages.scalars().all()

    @staticmethod
    async def get_message_count(
        email_conversation_id: uuid.UUID,
    ) -> int:
        """
        Get the total number of messages in a conversation.
        """
        query = select(func.count(ChatMessage.id)).where(
            ChatMessage.email_conversation_id == email_conversation_id
        )
        async with async_session() as session:
            result = await session.execute(query)
            return result.scalar() or 0
