import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(level=logging.INFO)


def send_email(
        smtp_server, smtp_port,
        sender_email, sender_password,
        receiver_emails,
        subject, body):
    # MIME object to represent the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)  # Email server
        server.starttls()  # Connection using TLS
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_emails, msg.as_string())
        logging.info("Mails sent successfully")
    except Exception as e:
        logging.error(f"Sending error: {e}")
    finally:
        server.quit()
