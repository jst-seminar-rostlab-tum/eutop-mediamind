import re
from uuid import UUID

from app.core.config import get_configs
from app.core.logger import get_logger
from app.models.email_conversation import EmailConversation
from app.repositories.chatbot_repository import ChatbotRepository
from app.schemas.chatbot_schemas import ChatRequest
from app.schemas.user_schema import UserEntity
from app.services.chatbot_service import ChatbotContext, ChatbotEmailSending
from app.services.chatbot_service.chatbot_response import ChatbotResponse
from app.services.s3_service import S3Service

configs = get_configs()
logger = get_logger(__name__)


class ChatbotService:
    @staticmethod
    async def extract_conversation_id_from_subject(
        subject: str, user: UserEntity
    ) -> UUID:
        """
        Extracts the conversation ID from the subject of the chat request
        in [conversation_id] format.
        """
        try:
            conversation_id_match = re.search(r"\[([^\[\]]+)\]", subject)
            if conversation_id_match is None:
                raise Exception(
                    f"Failed to generate chatbot email response for "
                    f"user_id={user.id}: failed to extract conversation_id "
                    "from subject. Sending default response."
                )
            return UUID(conversation_id_match.group(1))
        except Exception as e:
            await ChatbotEmailSending.send_context_not_found_response(
                user=user,
                subject=subject,
            )
            raise Exception(
                f"Failed to generate chatbot email response for "
                f"user_id={user.id}: couldn't create UUID from subject="
                f"{subject}; {e}."
            )

    @staticmethod
    async def check_max_message_limit(
        email_conversation: EmailConversation,
        user: UserEntity,
    ):
        message_count = await ChatbotRepository.get_message_count(
            email_conversation.id
        )
        if message_count >= configs.CHAT_MAX_MESSAGES_PER_CONVERSATION:
            await ChatbotEmailSending.send_message_limit_exceeded_response(
                user=user,
                subject=email_conversation.subject,
            )
            raise Exception(
                f"Conversation {email_conversation.id} has reached the "
                "maximum message limit "
                f"({configs.CHAT_MAX_MESSAGES_PER_CONVERSATION}). "
                f"Current count: {message_count}"
            )

    @staticmethod
    async def generate_and_send_email_response(
        user: UserEntity,
        chat: ChatRequest,
        s3_service: S3Service,
    ):
        conversation_id = (
            await ChatbotService.extract_conversation_id_from_subject(
                chat.subject, user
            )
        )
        email_conversation = (
            await ChatbotRepository.get_conversation_by_id_and_email(
                conversation_id, user.email
            )
        )

        if email_conversation is None:
            await ChatbotEmailSending.send_context_not_found_response(
                user=user,
                subject=chat.subject,
            )
            raise Exception(
                f"No conversation found with id={conversation_id} "
                f"for user {user.email}"
            )

        await ChatbotService.check_max_message_limit(email_conversation, user)

        report_file = report_file = (
            await ChatbotContext.load_report_pdf_file(
                s3_service=s3_service,
                report_id=email_conversation.report_id,
                user_id=user.id,
            )
            if email_conversation.report_id is not None
            else None
        )
        llm_response = await ChatbotResponse.generate(
            email_conversation_id=email_conversation.id,
            subject=email_conversation.subject,
            chat_body=chat.body,
            report_file=report_file,
        )
        await ChatbotContext.store_chat_messages(
            email_conversation.id, chat.body, llm_response
        )
        llm_response_as_html = ChatbotResponse.format(
            llm_response, user.first_name, user.language
        )
        await ChatbotEmailSending.send_email_response(
            email_conversation_id=email_conversation.id,
            user_email=user.email,
            subject=chat.subject,
            content=llm_response_as_html,
        )
