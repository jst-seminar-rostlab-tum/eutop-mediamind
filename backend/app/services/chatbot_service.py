from uuid import UUID

from app.core.config import configs
from app.core.logger import get_logger
from app.models.chat_message import MessageRole
from app.models.email import Email
from app.models.email_conversation import EmailConversation
from app.repositories.chatbot_repository import ChatbotRepository
from app.schemas.chatbot_schemas import ChatRequest
from app.schemas.user_schema import UserEntity
from app.services.email_service import EmailService

logger = get_logger(__name__)


class ChatbotService:
    @staticmethod
    async def get_or_create_conversation(
        user: UserEntity, chat: ChatRequest
    ) -> EmailConversation:
        email_conversation = (
            await ChatbotRepository.get_conversation_by_email_and_subject(
                user.email, chat.subject
            )
        )
        if not email_conversation:
            email_conversation = await ChatbotRepository.create_conversation(
                user.email, chat.subject
            )
        return email_conversation

    @staticmethod
    async def load_conversation_context(email_conversation_id: UUID) -> str:
        conversation_history = (
            await ChatbotRepository.get_conversation_history(
                email_conversation_id
            )
        )
        context_messages = []
        for message in conversation_history:
            context_messages.append(f"{message.role.value}: {message.content}")

        conversation_context = (
            "\n\n".join(context_messages)
            if len(context_messages) > 0
            else "No previous messages"
        )
        return conversation_context

    @staticmethod
    async def generate_and_add_assistant_message(
        email_conversation_id: UUID, user_first_name: str, chat: ChatRequest
    ) -> str:
        conversation_context = await ChatbotService.load_conversation_context(
            email_conversation_id
        )
        chatbot_response = f"""<p>Hi {user_first_name},</p>
            <div style="background-color: #f5f5f5; padding: 10px;
                margin: 10px 0;">
                <strong>Conversation History:</strong><br>
                <pre>{conversation_context}</pre>
            </div>
            <p><strong>Your latest message:</strong> {chat.body}</p>
            <p><strong>Subject:</strong> {chat.subject}</p>
            <p>This is a mock response.</p>
            <p>Best regards,<br>
            MediaMind Team</p>
            """
        await ChatbotRepository.add_message(
            email_conversation_id=email_conversation_id,
            role=MessageRole.ASSISTANT,
            content=chatbot_response,
        )
        return chatbot_response

    @staticmethod
    async def send_email_response(
        email_conversation_id, user_email: str, subject: str, content: str
    ):
        email = Email(
            sender=configs.SMTP_USER,
            recipient=user_email,
            subject=f"[MEDIAMIND]: {subject}",
            content_type="text/HTML",
            content=content,
        )

        try:
            EmailService.send_ses_email(email)
            logger.info(
                f"Chat response sent to {user_email} for "
                f"email_conversation {email_conversation_id}"
            )
        except Exception as e:
            logger.error(f"Failed to send email to {user_email}: {str(e)}")
            raise e

    @staticmethod
    async def generate_and_send_email_response(
        user: UserEntity, chat: ChatRequest
    ):
        email_conversation: EmailConversation = (
            await ChatbotService.get_or_create_conversation(user, chat)
        )
        await ChatbotRepository.add_message(
            email_conversation_id=email_conversation.id,
            role=MessageRole.CUSTOMER,
            content=chat.body,
        )
        chatbot_response = (
            await ChatbotService.generate_and_add_assistant_message(
                email_conversation_id=email_conversation.id,
                user_first_name=user.first_name,
                chat=chat,
            )
        )
        await ChatbotService.send_email_response(
            email_conversation_id=email_conversation.id,
            user_email=user.email,
            subject=chat.subject,
            content=chatbot_response,
        )
