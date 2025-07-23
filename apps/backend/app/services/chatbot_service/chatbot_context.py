from io import BytesIO
from uuid import UUID

from app.core.logger import get_logger
from app.models.chat_message import MessageRole
from app.repositories.chatbot_repository import ChatbotRepository
from app.services.report_service import ReportService
from app.services.s3_service import S3Service
from app.services.web_harvester.breaking_news_crawler import (
    get_all_breaking_news,
)

logger = get_logger(__name__)


class ChatbotContext:
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
        report_pdf_bytes = await s3_service.download_fileobj(key=report.s3_key)
        report_pdf_file = BytesIO(report_pdf_bytes)
        report_pdf_file.name = f"report-{report.id}.pdf"
        return report_pdf_file

    @staticmethod
    def load_breaking_news() -> str:
        """
        Loads breaking news and returns it as a string.
        """
        try:
            breaking_news_raw = get_all_breaking_news()
            breaking_news = "\n".join(
                [
                    f"Title: {news.title}\nPublished at: {news.published_at}\n"
                    f"Summary: {news.summary}\nURL: {news.url}"
                    for news in breaking_news_raw
                ]
            )
            breaking_news = (
                f"Breaking news count: {len(breaking_news_raw)}\n\n"
                + breaking_news
            )
        except Exception as e:
            logger.error(
                f"Error loading breaking news for Chatbot context: {e}"
            )
            breaking_news = "Failed to retrieve breaking news."
        return breaking_news
