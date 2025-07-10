# flake8: noqa: E501
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import gmtime, strftime
from typing import List

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import configs
from app.core.logger import get_logger
from app.models.email import Email, EmailState
from app.repositories.email_repository import EmailRepository
from app.repositories.user_repository import UserRepository
from app.services.translation_service import ArticleTranslationService
from app.services.user_service import UserService

logger = get_logger(__name__)

templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
templates_env = Environment(
    loader=FileSystemLoader(templates_dir),
    autoescape=select_autoescape(["html"]),
)


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
    def send_ses_email(email: Email):
        """
        Send an email using AWS SES SMTP credentials from the chatbot config.
        """
        msg = MIMEMultipart("alternative")
        msg["From"] = configs.CHAT_SMTP_FROM
        msg["To"] = email.recipient
        msg["Subject"] = email.subject

        html = MIMEText(email.content, "html")
        msg.attach(html)

        with smtplib.SMTP_SSL(
            configs.CHAT_SMTP_SERVER, configs.CHAT_SMTP_PORT
        ) as smtp_server:
            smtp_server.login(
                configs.CHAT_SMTP_USER, configs.CHAT_SMTP_PASSWORD
            )
            ok = smtp_server.sendmail(
                configs.CHAT_SMTP_FROM, email.recipient, msg.as_string()
            )
            if not (ok == {}):
                raise Exception(f"Error sending SES email: {ok}")

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
    def _render_email_template(template_name: str, context: dict) -> str:
        try:
            template = templates_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {str(e)}")
            raise

    @staticmethod
    def _build_email_content(
        s3_link: str,
        dashboard_link: str,
        profile_name: str,
        last_name: str,
        language: str = "en",
    ) -> str:
        translator = ArticleTranslationService.get_translator(language)

        month = strftime("%B", gmtime())
        month_translated = translator(month)
        day = strftime("%d", gmtime())
        year = strftime("%Y", gmtime())

        today = f"{month_translated} {int(day)}, {year}"

        greeting = translator("Good morning")
        if last_name:
            title = translator("Mr./Ms.")
            salutation = f"{greeting}, {title} {last_name}"
        else:
            salutation = f"{greeting},"

        context = {
            "s3_link": s3_link,
            "dashboard_link": dashboard_link,
            "profile_name": profile_name,
            "date": today,
            "language_code": language,
            "title": translator("Daily News Report"),
            "search_profile": translator("Search Profile"),
            "salutation": salutation,
            "text_1": translator(
                "This is your daily news report, carefully picked to match "
                "your specific interests and search criteria. Our system has "
                "identified the most relevant developments in your field, "
                "ensuring you stay informed with the insights that matter to "
                "your business"
            ),
            "text_2": translator(
                "Each story has been selected based on its relevance to your "
                "profile, providing you with a comprehensive overview of "
                "today's key developments"
            ),
            "download_text": translator("Download here"),
            "text_3": translator(
                "After that, you can still access your report anytime "
                "via your dashboard"
            ),
            "click_text": translator("click here"),
            "text_4": translator(
                "If the link above does not work, copy and paste this URL "
                "into your browser"
            ),
            "deliver_text": translator("Delivered by MediaMind"),
        }

        template_name = "email_template.html"

        return EmailService._render_email_template(template_name, context)

    @staticmethod
    def _get_report_in_user_language(reports, user):
        english_report = None
        for report in reports:
            if report["report"].language == user.language:
                return report
            if report["report"].language == "en":
                english_report = report
        # If there is no report in the user language
        return english_report

    @staticmethod
    async def run(reports_infos: List[dict]):
        grouped_reports = {}
        for report in reports_infos:
            search_profile_id = report["search_profile"].id
            if search_profile_id not in grouped_reports:
                grouped_reports[search_profile_id] = []
            grouped_reports[search_profile_id].append(report)

        for search_profile_id, reports in grouped_reports.items():
            search_profile = reports[0]["search_profile"]
            try:
                for email in search_profile.organization_emails:
                    user = await UserService.get_by_email(email)
                    report_in_user_lang = (
                        EmailService._get_report_in_user_language(
                            reports, user
                        )
                    )

                    report = report_in_user_lang["report"]
                    presigned_url = report_in_user_lang["presigned_url"]
                    dashboard_url = report_in_user_lang["dashboard_url"]

                    translator = ArticleTranslationService.get_translator(
                        user.language
                    )
                    time_slot_translated = translator(
                        report.time_slot.capitalize()
                    )
                    subject = (
                        f"[MEDIAMIND] {translator('Your')} {time_slot_translated} "
                        f"{translator('Report')} {translator('for')} {search_profile.name}"
                    )
                    email_schedule = EmailSchedule(
                        recipient=email,
                        subject=subject,
                        content_type="text/HTML",
                        content=EmailService._build_email_content(
                            presigned_url,
                            dashboard_url,
                            search_profile.name,
                            user.last_name,
                            user.language,
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
