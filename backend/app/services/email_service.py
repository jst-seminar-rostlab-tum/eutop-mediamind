from app.core.config import configs
from app.core.logger import get_logger
from app.models.email import Email, EmailState
from app.repositories.email_repository import EmailRepository
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment
from sendgrid import SendGridAPIClient

logger = get_logger(__name__)

class EmailSchedule:
    def __init__(self, recipient: str, subject: str, content_type: str, content: str, attachment: str) -> None:
        self.recipient = recipient
        self.sub = subject
        self.content = content
        self.content_type = content_type
        self.attachment = attachment

class EmailService:
    __sg_client= SendGridAPIClient(api_key=configs.SENDGRID_KEY)

    @staticmethod
    def schedule_email(schedule: EmailSchedule) -> Email:
        email = Email()
        email.sender = configs.SENDER_EMAIL
        email.recipient = schedule.recipient
        email.subject = schedule.sub
        email.content_type = schedule.content_type
        email.content = schedule.content
        email.attachment = schedule.attachment

        return EmailRepository.add_email(email)

    @staticmethod
    def send_scheduled_emails():
        emails = EmailRepository.get_all_unsent_emails()

        for email in emails:
            try:
                EmailService.__send_email(email)
                email.state = EmailState.SENT
                EmailRepository.update_email(email)
            except Exception as e:
                logger.error(f"Failed to send email to {email.recipient}: {str(e)}")
                email.attempts += 1
                email.add_error(str(e))
                if email.attempts >= configs.MAX_EMAIL_ATTEMPTS:
                    email.state = EmailState.FAILED
                else:
                    email.state = EmailState.RETRY
                EmailRepository.update_email(email)


    @staticmethod
    def __send_email(schedule: EmailSchedule):
        from_email = Email(configs.SENDER_EMAIL)  
        to_email = To(schedule.recipient)  
        content = Content(schedule.content_type, schedule.content)
        attachment = Attachment(schedule.attachment, "report.pdf", "application/pdf", "attachment")

        mail = Mail(from_email, to_email, schedule.sub, content)
        mail.add_attachment(attachment)

        response = EmailService.__sg_client.client.mail.send.post(request_body=mail.get())

        if response.status_code >= 300:
            raise Exception(f"Failed to send email: {response.status_code} - {response.body.decode('utf-8')}")






