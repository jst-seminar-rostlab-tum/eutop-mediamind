from app.core.config import configs
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment
from sendgrid import SendGridAPIClient


class EmailSchedule:
    def __init__(self, sender_email: str, receiver: str, subject: str, content_type: str, content: str, attachment: str) -> None:
        self.sender = sender_email
        self.receiver = receiver
        self.sub = subject
        self.content = content
        self.content_type = content_type
        self.attempts = 0
        self.attachment = attachment

class EmailService():
    def __init__(self) -> None:
        self.sg_client= SendGridAPIClient(api_key=configs.SENDGRID_KEY)

    def sendEmail(self, schedule: EmailSchedule) -> bool:
        from_email = Email(schedule.sender)  
        to_email = To(schedule.receiver)  
        content = Content(schedule.content_type, schedule.content)
        attachment = Attachment(schedule.attachment, "report.pdf", "application/pdf", "attachment")

        mail = Mail(from_email, to_email, schedule.sub, content)
        mail.add_attachment(attachment)

        response = self.sg_client.client.mail.send.post(request_body=mail.get())

        return response.status_code == 202





