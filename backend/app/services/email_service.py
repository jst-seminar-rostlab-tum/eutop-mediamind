# flake8: noqa: E501

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import gmtime, strftime
from typing import List

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

    @staticmethod
    async def run(reports_infos: List[dict]):
        for reports_info in reports_infos:
            report = reports_info["report"]
            presigned_url = reports_info["presigned_url"]
            dashboard_url = reports_info["dashboard_url"]
            search_profile = reports_info["search_profile"]
            try:
                for email in search_profile.organization_emails:
                    email_schedule = EmailSchedule(
                        recipient=email,
                        subject=f"[MEDIAMIND] Your "
                        f"{report.time_slot.capitalize()}"
                        f"Report for {search_profile.name}",
                        content_type="text/HTML",
                        content=EmailService._build_email_content(
                            presigned_url, dashboard_url, search_profile.name
                        ),
                    )

                    await EmailService.schedule_email(email_schedule)
                    await EmailService.send_scheduled_emails()
                logger.info(
                    f"Email scheduling done for report {search_profile.name}"
                )
            except Exception as e:
                logger.error(f"Error in EmailService: {str(e)}")
                continue

    @staticmethod
    def _build_email_content(
        s3_link: str, dashboard_link: str, profile_name: str
    ) -> str:
        today = strftime("%B %d, %Y", gmtime())

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Daily News Report</title>
<style>
    @media only screen and (max-width: 650px) {{
    .main-table {{
        width: 100% !important;
        max-width: 100% !important;
        border-radius: 0 !important;
        padding: 0 !important;
    }}
    .content-cell {{
        padding: 24px 8px !important;
    }}
    .header-cell {{
        padding: 16px 10px !important;
    }}
    .footer-cell {{
        padding: 18px 10px !important;
    }}
    .profile-section {{
        padding-bottom: 12px !important;
        margin-bottom: 16px !important;
    }}
    .download-btn {{
        font-size: 1em !important;
        padding: 10px 16px !important;
    }}
    }}
</style>
</head>
<body style="margin:0; padding:0; background-color:#f8f9fa; font-family:Helvetica, Arial, sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="padding:40px 0;">
    <tr>
    <td align="center">
        <table class="main-table" width="600" cellpadding="0" cellspacing="0" border="0" style="width:100%; max-width:600px; background-color:#fff; border-radius:8px; box-shadow:0 4px 20px rgba(0,0,0,0.08); overflow:hidden;">
        <!-- Header -->
        <tr>
            <td class="header-cell" style="background-color:#4b99ff; padding:20px 35px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                <td align="left" style="color:#fff;">
                    <h1 style="margin:0; font-size:2.1em; font-weight:300; letter-spacing:-0.5px; line-height:1.2;">MediaMind</h1>
                    <p style="margin:12px 0 0; font-size:0.9em; text-transform:uppercase; letter-spacing:0.5px; color:rgba(255,255,255,0.85);">{today}</p>
                </td>
                <td align="right" style="vertical-align:top;">
                    <img src="https://mediamind.csee.tech/EUTOP_Logo.png" alt="Logo" width="120" style="display:block;max-width:120px;width:100%;" />
                </td>
                </tr>
            </table>
            </td>
        </tr>
        <!-- Divider -->
        <tr>
            <td style="height:4px; background:linear-gradient(90deg,#1e5091 0%,#ffd700 100%);"></td>
        </tr>
        <!-- Content -->
        <tr>
            <td class="content-cell" style="padding:50px 40px; color:#2c3e50;">
            <!-- Profile section -->
            <div class="profile-section" style="margin-bottom:25px; padding-bottom:25px; border-bottom:1px solid #e9ecef;">
                <p style="color:#6c757d; font-size:0.95em; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px; font-weight:500;">Search Profile</p>
                <p style="color:#1e5091; font-size:1.2em; font-weight:600; margin:0;">{profile_name}</p>
            </div>
            <!-- Message -->
            <div style="font-size:1.05em; line-height:1.65; color:#495057; font-weight:400;">
                <p style="margin:0 0 18px 0;">
                Good morning,<br /><br />
                This is your <span style="color:#1e5091; font-weight:600;">daily news report</span>,
                carefully curated to match your specific interests and search criteria.
                Our monitoring system has identified the most relevant developments in your field,
                ensuring you stay informed with <span style="color:#1e5091; font-weight:600;">actionable insights</span>
                that matter to your business.<br /><br />
                Each story has been selected based on its relevance to your profile,
                providing you with a comprehensive overview of today's key developments.
                </p>
                <div style="text-align:center; margin: 32px 0 24px 0;">
                <a class="download-btn" style="
                    color: #fff; 
                    background: #1e5091;
                    font-weight: 700;
                    text-decoration: none;
                    padding: 12px 32px;
                    border-radius: 5px;
                    box-shadow: 0 2px 8px rgba(30,80,145,0.10);
                    display: inline-block;
                    font-size: 1.08em;
                    transition: background 0.2s;
                    word-break:break-word;
                " href="{s3_link}" target="_blank">
                    Download here
                </a>
                </div>
                <div style="margin-bottom:25px; padding-bottom:25px; border-bottom:1px solid #e9ecef;">
                <b>Note:</b> The download link expires after 7 days. After that, you can still access your report anytime via your dashboard (<a style="font-weight:600; color:#1e5091" href="{dashboard_link}">click here</a>).
                </div>
                <div style="color:#888; font-size:0.9em;">
                If the link above does not work, copy and paste this URL into your browser:<br />
                <span style="font-size:0.7em; word-break:break-all; display:inline-block; margin-top:4px;"><u><a href="{s3_link}" style="color:#888;">{s3_link}</a></u></span>
                </div>
            </div>
            </td>
        </tr>
        <!-- Footer -->
        <tr>
            <td class="footer-cell" style="background-color:#f8f9fa; padding:30px 40px; text-align:center; border-top:1px solid #e9ecef;">
            <div style="width:60px; height:2px; background-color:#ffd700; margin:0 auto 20px;"></div>
            <p style="color:#6c757d; font-size:0.9em; font-weight:400; margin:0;">Delivered by MediaMind</p>
            </td>
        </tr>
        </table>
    </td>
    </tr>
</table>
</body>
</html>
"""
