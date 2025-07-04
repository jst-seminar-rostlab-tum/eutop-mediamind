from app.core.config import configs
from app.core.logger import get_logger
from app.models.email import Email
from app.schemas.chatbot_schemas import ChatRequest
from app.schemas.user_schema import UserEntity
from app.services.email_service import EmailService

logger = get_logger(__name__)


class ChatbotService:
    @staticmethod
    async def send_response(user: UserEntity, chat: ChatRequest):
        content = f"""<p>Hi {user.first_name},</p>
            Congratulations on using the slowest, most unsecure and least
            scalable web chatbot in the world!</p>
            <p><strong>Subject:</strong> {chat.subject}</p>
            <p><strong>Message:</strong> {chat.body}</p>
            Plese use chatgpt, claude, or any other AI chatbot instead:
            <p><a href="https://chat.openai.com/">ChatGPT</a> |
            <a href="https://claude.ai/">Claude</a> |
            <a href="https://www.bing.com/chat">Bing Chat</a></p>
            <p>Best regards,<br>
            MediaMind Team</p>
            <p><small>This is an automated reply. Please do not reply to
            this email.</small></p>
            """

        email = Email(
            sender=configs.SMTP_USER,
            recipient=user.email,
            subject=f"[MEDIAMIND]: {chat.subject}",
            content_type="text/HTML",
            content=content,
        )

        try:
            EmailService.send_ses_email(email)
            logger.info(
                f"Chat response sent to {user.email} with the"
                f"following attributes: sender = {chat.sender}, "
                f"subject = {chat.subject}, body = {chat.body}, "
                f"s3_key = {chat.s3_key}, bucket = {chat.bucket}."
            )
        except Exception as e:
            logger.error(f"Failed to send email to {user.email}: {str(e)}")
            raise e
