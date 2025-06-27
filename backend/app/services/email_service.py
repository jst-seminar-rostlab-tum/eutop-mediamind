import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
    ) -> None:
        self.recipient = recipient
        self.subject = subject
        self.content = content
        self.content_type = content_type


class EmailService:

    @staticmethod
    async def schedule_email(schedule: EmailSchedule) -> Email:
        email = Email()
        email.sender = configs.SMTP_USER
        email.recipient = schedule.recipient
        email.subject = schedule.subject
        email.content_type = schedule.content_type
        email.content = schedule.content

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
                email.add_error(str(e))
                if email.attempts >= configs.MAX_EMAIL_ATTEMPTS:
                    email.state = EmailState.FAILED
                else:
                    email.state = EmailState.RETRY
                await EmailRepository.update_email(email)
                raise Exception(
                    f"Failed to send email to {email.recipient}: {str(e)}"
                )

    @staticmethod
    def __send_email(email: Email):
        msg = MIMEMultipart("alternative")
        msg["From"] = email.sender
        msg["To"] = email.recipient
        msg["Subject"] = email.subject

        html = MIMEText(email.content, "html")
        msg.attach(html)

        with smtplib.SMTP_SSL(
            configs.SMTP_SERVER, configs.SMTP_PORT
        ) as smtp_server:
            smtp_server.login(configs.SMTP_USER, configs.SMTP_PASSWORD)
            ok = smtp_server.sendmail(
                email.sender, email.recipient, msg.as_string()
            )
            if not (ok == {}):
                raise Exception(f"Error sending email: {ok}")
