import asyncio
import re
from io import BytesIO
from uuid import UUID

import markdown

from app.core.config import configs
from app.core.logger import get_logger
from app.models.chat_message import MessageRole
from app.models.email import Email
from app.models.email_conversation import EmailConversation
from app.repositories.chatbot_repository import ChatbotRepository
from app.schemas.chatbot_schemas import ChatRequest
from app.schemas.user_schema import UserEntity
from app.services.email_service import EmailService
from app.services.llm_service.llm_client import LLMClient
from app.services.llm_service.llm_models import LLMModels
from app.services.report_service import ReportService
from app.services.s3_service import S3Service

logger = get_logger(__name__)


class ChatbotService:
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
    async def create_prompt_from_context(
        email_conversation_id: UUID, subject: str, chat_body: str
    ) -> str:
        conversation_context = await ChatbotService.load_conversation_context(
            email_conversation_id
        )
        prompt = f"""You are a professional customer support assistant for \
MediaMind, responding to user emails. Your tone must always be polite, \
empathetic, and solution-oriented. Your task is to provide a concise, \
professional, and helpful reply to the user's latest message. Find attached \
the PDF report related to the conversation, which contains relevant \
information that can help you answer the user's query.

Additionally, you can find the complete conversation history so far below. \
Messages are labelled as "user" (for user messages) and "assistant" \
(for your responses):

---
Subject: <{subject}>

{conversation_context}
---

The user's latest message is:
---
{chat_body}
---

Instructions:
- Respond only with the body of your reply, in clear and concise paragraphs.
- Do not include greetings, salutations, subject lines, or closing statements.
- Do not repeat or quote the user's message.
- Do not use emojis or informal language.
- If the user's message is unclear, politely ask for clarification.
- If you do not know the answer, reply that to the user and politely ask for \
more context.
- Attached you will find the latest report in PDF format. Use it to \
provide accurate information.
- Focus on providing accurate, actionable, and relevant information to \
resolve the user's query.
- Always answer in the language of the user's last message."""
        return prompt

    @staticmethod
    async def generate_llm_response(
        email_conversation_id: UUID,
        subject: str,
        chat_body: str,
        report_file: BytesIO,
    ) -> str:
        prompt = await ChatbotService.create_prompt_from_context(
            email_conversation_id=email_conversation_id,
            subject=subject,
            chat_body=chat_body,
        )

        llm_client = LLMClient(LLMModels.openai_4o_mini)
        try:
            llm_response = await asyncio.to_thread(
                llm_client.generate_response,
                prompt=prompt,
                file=report_file,
                temperature=0.7,
            )
        except Exception as e:
            logger.error(
                f"Error generating Chatbot response for email_conversation "
                f"with id={email_conversation_id} response: {str(e)}"
            )
            llm_response = f"""Thank you for your message regarding "\
{subject}". Unfortunately, we ran into a problem generating a response. \
Please try again later or contact us."""
        return llm_response

    @staticmethod
    async def send_email_response(
        email_conversation_id, user_email: str, subject: str, content: str
    ):
        email = Email(
            sender=configs.SMTP_USER,
            recipient=user_email,
            subject=subject,
            content_type="text/HTML",
            content=content,
        )

        try:
            await EmailService.send_ses_email(email)
            logger.info(
                f"Chat response sent to {user_email} for "
                f"email_conversation with id={email_conversation_id}"
            )
        except Exception as e:
            logger.error(
                f"Failed to send email to {user_email} for "
                f"email_conversation with id={email_conversation_id}: "
                f"{str(e)}"
            )
            raise e

    @staticmethod
    def format_llm_response(llm_response: str, user_first_name: str) -> str:
        llm_response_as_html = markdown.markdown(
            llm_response, extensions=["extra"]
        )
        email_as_html = f"""<p>Hi {user_first_name},</p>
            <p>{llm_response_as_html}</p>
            <p>Best regards,<br>
            MediaMind Team</p>
            """
        return email_as_html

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
    def extract_report_id(subject: str, user_id: UUID) -> UUID:
        """
        Extracts the report ID from the subject of the chat request
        in [report_id] format.
        """

        try:
            report_id_match = re.search(r"\[([^\[\]]+)\]", subject)
            if report_id_match is None:
                raise Exception("No report_id found in the subject.")
            return UUID(report_id_match.group(1))
        except Exception as e:
            raise Exception(
                f"Failed to generate chatbot email response for "
                f"user_id={user_id}: couldn't create UUID from subject="
                f"{subject}; {e}."
            )

    @staticmethod
    async def get_report_pdf_file(
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

    @staticmethod
    async def generate_and_send_email_response(
        user: UserEntity, chat: ChatRequest, s3_service: S3Service
    ):
        subject = chat.subject or "MediaMind Email-Chatbot"
        report_id = ChatbotService.extract_report_id(
            subject=subject, user_id=user.id
        )
        email_conversation: EmailConversation = (
            await ChatbotService.get_or_create_conversation(
                user_email=user.email,
                report_id=report_id,
                subject=subject,
            )
        )
        report_pdf_file = await ChatbotService.get_report_pdf_file(
            s3_service=s3_service, report_id=report_id, user_id=user.id
        )
        llm_response = await ChatbotService.generate_llm_response(
            email_conversation_id=email_conversation.id,
            subject=subject,
            chat_body=chat.body,
            report_file=report_pdf_file,
        )
        await ChatbotService.store_chat_messages(
            email_conversation.id, chat.body, llm_response
        )
        llm_response_as_html = ChatbotService.format_llm_response(
            llm_response, user.first_name
        )
        await ChatbotService.send_email_response(
            email_conversation_id=email_conversation.id,
            user_email=user.email,
            subject=subject,
            content=llm_response_as_html,
        )
