from uuid import UUID

from app.core.config import get_configs
from app.core.logger import get_logger
from app.models.email import Email
from app.schemas.user_schema import UserEntity
from app.services.email_service import EmailService

configs = get_configs()
logger = get_logger(__name__)


class ChatbotEmailSending:
    @staticmethod
    async def send_email_response(
        email_conversation_id: UUID | None,
        user_email: str,
        subject: str,
        content: str,
        report_id: UUID | None = None,
    ):
        email = Email(
            sender=configs.SMTP_FROM,
            recipient=user_email,
            subject=subject,
            content_type="text/HTML",
            content=content,
            report_id=report_id,
        )

        try:
            await EmailService.send_email(email)
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
    async def send_context_not_found_response(user: UserEntity, subject: str):
        """
        Sends a default error response to the user when the context couldn't
        be found. Users can only use the chatbot to reply to previously sent
        emails from us to them.
        """
        content = f"""<p>Hi {user.first_name},</p>
            <p>We couldn't find the context for your request. \
                Please make sure you are replying to an email \
                sent by us.</p>
            <p>Best regards,<br>
            MediaMind Team</p>"""
        await ChatbotEmailSending.send_email_response(
            email_conversation_id=None,
            user_email=user.email,
            subject=subject,
            content=content,
        )

    @staticmethod
    async def send_message_limit_exceeded_response(
        user: UserEntity, subject: str
    ):
        """
        Sends an error response to the user when the conversation has
        reached the maximum number of messages (100).
        """
        content = f"""<p>Hi {user.first_name},</p>
            <p>This conversation has reached the maximum number of messages \
allowed ({configs.CHAT_MAX_MESSAGES_PER_CONVERSATION} messages). To continue \
receiving support, please start a new conversation by replying to a different \
report email or contacting us directly.</p>
            <p>Best regards,<br>
            MediaMind Team</p>"""
        await ChatbotEmailSending.send_email_response(
            email_conversation_id=None,
            user_email=user.email,
            subject=subject,
            content=content,
        )
