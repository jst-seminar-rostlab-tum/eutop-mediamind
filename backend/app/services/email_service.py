from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Attachment,
    Content,
)
from sendgrid.helpers.mail import Email as SEmail
from sendgrid.helpers.mail import (
    Mail,
    To,
)

from app.core.config import configs
from app.core.logger import get_logger
from app.models.email import Email, EmailState
from app.repositories.email_repository import EmailRepository

logger = get_logger(__name__)


class EmailSchedule:
    def __init__(
        self,
        recipient: str,
        subject: str,
        content_type: str,
        content: str,
        attachment: str,
    ) -> None:
        self.recipient = recipient
        self.subject = subject
        self.content = content
        self.content_type = content_type
        self.attachment = attachment


class EmailService:
    __sg_client = SendGridAPIClient(api_key=configs.SENDGRID_KEY)

    @staticmethod
    async def schedule_email(schedule: EmailSchedule) -> Email:
        email = Email()
        email.sender = configs.SENDER_EMAIL
        email.recipient = schedule.recipient
        email.subject = schedule.subject
        email.content_type = schedule.content_type
        email.content = schedule.content
        email.attachment = schedule.attachment

        return await EmailRepository.add_email(email)

    @staticmethod
    async def send_scheduled_emails():
        emails = await EmailRepository.get_all_unsent_emails()

        for email in emails:
            try:
                email.attempts += 1
                EmailService.__send_email(email)
                email.state = EmailState.SENT
                await EmailRepository.update_email(email)
            except Exception as e:
                logger.error(
                    f"Failed to send email to {email.recipient}: {str(e)}"
                )
                email.add_error(str(e))
                if email.attempts >= configs.MAX_EMAIL_ATTEMPTS:
                    email.state = EmailState.FAILED
                else:
                    email.state = EmailState.RETRY
                await EmailRepository.update_email(email)

    @staticmethod
    def __send_email(email: Email):
        from_email = SEmail(configs.SENDER_EMAIL)
        to_email = To(email.recipient)
        content = Content(email.content_type, email.content)
        attachment = Attachment(
            email.attachment, "report.pdf", "application/pdf", "attachment"
        )

        mail = Mail(from_email, to_email, email.subject, content)
        mail.add_attachment(attachment)

        response = EmailService.__sg_client.client.mail.send.post(
            request_body=mail.get()
        )

        if response.status_code >= 300:
            raise Exception(
                f"Failed to send email: {response.status_code} - {response.body.decode('utf-8')}"
            )
