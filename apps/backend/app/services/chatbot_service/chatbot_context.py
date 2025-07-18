from io import BytesIO
from uuid import UUID

from app.core.logger import get_logger
from app.models.chat_message import MessageRole
from app.models.email_conversation import EmailConversation
from app.repositories.chatbot_repository import ChatbotRepository
from app.services.report_service import ReportService
from app.services.s3_service import S3Service

logger = get_logger(__name__)


class ChatbotContext:
    @staticmethod
    async def get_or_create_conversation(
        user_email: str, subject: str, report_id: UUID
    ) -> EmailConversation:
        email_conversation = (
            await ChatbotRepository.get_conversation_by_email_and_subject(
                user_email, subject
            )
        )
        if not email_conversation:
            email_conversation = await ChatbotRepository.create_conversation(
                user_email, subject, report_id
            )
        return email_conversation

    @staticmethod
    async def store_chat_messages(
        email_conversation_id: UUID, chat_body: str, llm_response: str
    ):
        await ChatbotRepository.add_message(
            email_conversation_id=email_conversation_id,
            role=MessageRole.USER,
            content=chat_body,
        )
        await ChatbotRepository.add_message(
            email_conversation_id=email_conversation_id,
            role=MessageRole.ASSISTANT,
            content=llm_response,
        )

    @staticmethod
    async def load_conversation_context(
        email_conversation_id: UUID,
    ) -> str | None:
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
            else None
        )
        return conversation_context

    @staticmethod
    async def load_report_pdf_file(
        s3_service: S3Service, report_id: UUID, user_id: UUID
    ) -> BytesIO:
        """
        Downloads the report PDF file from S3 and returns it as a BytesIO
        object.
        """
        report = await ReportService.get_report_by_id(report_id)
        if report is None:
            raise Exception(
                f"Failed to generate chatbot email response for "
                f"user_id={user_id}: report with id={report_id} not found."
            )
        if report.s3_key is None:
            raise Exception(
                f"Failed to generate chatbot email response for "
                f"user_id={user_id}: s3_key missing for report with "
                f"id={report_id}."
            )
        report_pdf_bytes = await s3_service.download_file(
            filename=str(report.id), key=report.s3_key
        )
        report_pdf_file = BytesIO(report_pdf_bytes)
        report_pdf_file.name = f"report-{report.id}.pdf"
        return report_pdf_file
