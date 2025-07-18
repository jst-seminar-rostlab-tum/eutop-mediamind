import re
from uuid import UUID

from app.core.logger import get_logger
from app.models.email_conversation import EmailConversation
from app.schemas.chatbot_schemas import ChatRequest
from app.schemas.user_schema import UserEntity
from app.services.chatbot_service import ChatbotContext, ChatbotEmailSending
from app.services.chatbot_service.chatbot_response import ChatbotResponse
from app.services.s3_service import S3Service

logger = get_logger(__name__)


class ChatbotService:
    @staticmethod
    def extract_report_id_from_subject(subject: str, user_id: UUID) -> UUID:
        """
        Extracts the report ID from the subject of the chat request
        in [report_id] format.
        """
        try:
            report_id_match = re.search(r"\[([^\[\]]+)\]", subject)
            if report_id_match is None:
                raise Exception(
                    f"Failed to generate chatbot email response for "
                    f"user_id={user_id}: failed to extract report_id "
                    "from subject. Sending default response."
                )
            return UUID(report_id_match.group(1))
        except Exception as e:
            raise Exception(
                f"Failed to generate chatbot email response for "
                f"user_id={user_id}: couldn't create UUID from subject="
                f"{subject}; {e}."
            )

    @staticmethod
    async def generate_and_send_email_response(
        user: UserEntity,
        chat: ChatRequest,
        s3_service: S3Service,
    ):
        subject = (
            chat.subject if chat.subject != "" else "MediaMind Email-Chatbot"
        )
        try:
            report_id = ChatbotService.extract_report_id_from_subject(
                chat.subject, user.id
            )
        except Exception as e:
            await ChatbotEmailSending.send_context_not_found_response(
                user=user,
                subject=chat.subject,
            )
            raise Exception(str(e))

        email_conversation: EmailConversation = (
            await ChatbotContext.get_or_create_conversation(
                user_email=user.email,
                report_id=report_id,
                subject=subject,
            )
        )
        report_pdf_file = await ChatbotContext.load_report_pdf_file(
            s3_service=s3_service, report_id=report_id, user_id=user.id
        )
        llm_response = await ChatbotResponse.generate(
            email_conversation_id=email_conversation.id,
            subject=subject,
            chat_body=chat.body,
            report_file=report_pdf_file,
        )
        await ChatbotContext.store_chat_messages(
            email_conversation.id, chat.body, llm_response
        )
        llm_response_as_html = ChatbotResponse.format(
            llm_response, user.first_name
        )
        await ChatbotEmailSending.send_email_response(
            email_conversation_id=email_conversation.id,
            user_email=user.email,
            subject=subject,
            content=llm_response_as_html,
        )
