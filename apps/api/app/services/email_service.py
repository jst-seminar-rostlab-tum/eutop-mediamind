# flake8: noqa: E501
import os
import uuid
import smtplib
from datetime import datetime, timezone
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logging import error
from time import gmtime, strftime
from typing import List

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import configs
from app.core.languages import Language
from app.core.logger import get_logger
from app.models.breaking_news import BreakingNews
from app.models.email import Email, EmailState
from app.models.user import Gender
from app.repositories.email_repository import EmailRepository
from app.repositories.organization_repository import OrganizationRepository
from app.services.translation_service import ArticleTranslationService
from app.services.user_service import UserService
from app.services.s3_service import S3Service, get_s3_service

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
        report_id: uuid.UUID,
    ) -> None:
        self.recipient = recipient
        self.subject = subject
        self.content = content
        self.content_type = content_type
        self.report_id = report_id


class EmailService:

    @staticmethod
    def create_email(
        recipient: str,
        subject: str,
        content_type: str,
        content: str,
        report_id: uuid.UUID,
    ) -> Email:
        email = Email(
            sender=configs.SMTP_USER,
            recipient=recipient,
            subject=subject,
            content_type=content_type,
            content=content,
            report_id=report_id,
        )
        return email

    @staticmethod
    async def schedule_email(schedule: EmailSchedule) -> Email:
        email = EmailService.create_email(
            recipient=schedule.recipient,
            subject=schedule.subject,
            content_type=schedule.content_type,
            content=schedule.content,
            report_id=schedule.report_id
        )
        return await EmailRepository.add_email(email)

    @staticmethod
    async def send_scheduled_emails() -> None:
        emails = await EmailRepository.get_all_unsent_emails()
        s3_service = get_s3_service()

        for email in emails:
            try:
                email.attempts += 1
                pdf_as_link = (
                    await OrganizationRepository.get_pdf_as_link_by_recipient(
                        email.recipient
                    )
                )
                pdf_bytes = None
                if not pdf_as_link and email.report.s3_key:
                    pdf_bytes = await s3_service.download_fileobj(email.report.s3_key)
                EmailService.send_email(email, pdf_bytes)
                email.state = EmailState.SENT
                await EmailRepository.update_email(email)
            except Exception as e:
                email.add_error(str(e))
                if email.attempts >= configs.MAX_EMAIL_ATTEMPTS:
                    email.state = EmailState.FAILED
                else:
                    email.state = EmailState.RETRY
                await EmailRepository.update_email(email)
                raise RuntimeError(
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
    def send_email(
        email: Email, pdf_bytes: bytes = None, bcc_recipients: List[str] = None
    ):
        msg = MIMEMultipart("alternative")
        msg["From"] = email.sender
        msg["To"] = email.recipient
        msg["Subject"] = email.subject

        # BCC recipients are not added to the message headers for privacy
        # They are only included in the sendmail call
        html = MIMEText(email.content, "html")
        msg.attach(html)

        if pdf_bytes:
            attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
            attachment.add_header(
                "Content-Disposition", "attachment", filename="report.pdf"
            )
            msg.attach(attachment)

        # Only add BCC if there are recipients
        all_recipients = []
        if bcc_recipients:
            all_recipients.extend(bcc_recipients)
        else:
            all_recipients.append(email.recipient)

        with smtplib.SMTP_SSL(
            configs.SMTP_SERVER, configs.SMTP_PORT
        ) as smtp_server:
            smtp_server.login(configs.SMTP_USER, configs.SMTP_PASSWORD)
            ok = smtp_server.sendmail(
                email.sender, all_recipients, msg.as_string()
            )
            if not (ok == {}):
                error_msg = "Error sending email"
                if bcc_recipients:
                    error_msg += " with BCC"
                raise Exception(f"{error_msg}: {ok}")

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
        gender: Gender,
        language: str = Language.EN.value,
        pdf_as_link: bool = True,
    ) -> str:
        translator = ArticleTranslationService.get_translator(language)

        month = strftime("%B", gmtime())
        month_translated = translator(month)
        day = strftime("%d", gmtime())
        year = strftime("%Y", gmtime())

        today = f"{month_translated} {int(day)}, {year}"

        greeting = translator("Good morning")
        if last_name and gender:
            if gender == Gender.male:
                title = translator("Mr.")
            elif gender == Gender.female:
                title = translator("Ms.")
            else:
                title = "Mx."
            salutation = f"{greeting}, {title} {last_name}"
        else:
            salutation = f"{greeting}"

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
            "text_3_link_true": translator(
                "After that, you can still access your report anytime "
                "via your dashboard"
            ),
            "text_3_link_false": translator(
                "We have attached your PDF report to this email for your convenience"
            ),
            "click_text": translator("click here"),
            "text_4": translator(
                "If the link above does not work, copy and paste this URL "
                "into your browser"
            ),
            "deliver_text": translator("Delivered by MediaMind"),
            "pdf_as_link": pdf_as_link,
        }

        template_name = "email_template.html"

        return EmailService._render_email_template(template_name, context)

    @staticmethod
    def _build_breaking_news_email_content(news: BreakingNews) -> str:
        published_at_utc = news.published_at
        if isinstance(published_at_utc, str):
            published_at_utc = datetime.fromisoformat(published_at_utc)
        if published_at_utc.tzinfo is None:
            published_at_utc = published_at_utc.replace(tzinfo=timezone.utc)
        else:
            published_at_utc = published_at_utc.astimezone(timezone.utc)

        published_at = published_at_utc.strftime("%d.%m.%Y, %H:%M")
        current_time = datetime.now(timezone.utc).strftime("%d.%m.%Y, %H:%M")

        context = {
            "news_title": news.title,
            "news_summary": news.summary,
            "news_date": published_at,
            "news_url": news.url,
            "date_time": current_time,
        }

        template_name = "breaking_news_template.html"

        return EmailService._render_email_template(template_name, context)

    @staticmethod
    def _build_breaking_news_email_content(news: BreakingNews) -> str:
        published_at_utc = news.published_at
        if isinstance(published_at_utc, str):
            published_at_utc = datetime.fromisoformat(published_at_utc)
        if published_at_utc.tzinfo is None:
            published_at_utc = published_at_utc.replace(tzinfo=timezone.utc)
        else:
            published_at_utc = published_at_utc.astimezone(timezone.utc)

        published_at = published_at_utc.strftime("%d.%m.%Y, %H:%M")
        current_time = datetime.now(timezone.utc).strftime("%d.%m.%Y, %H:%M")

        context = {
            "news_title": news.title,
            "news_summary": news.summary,
            "news_date": published_at,
            "news_url": news.url,
            "date_time": current_time,
        }

        template_name = "breaking_news_template.html"

        return EmailService._render_email_template(template_name, context)

    @staticmethod
    def _get_report_in_user_language(reports, user, search_profile_language):
        sp_language_report = None
        english_report = None
        for report in reports:
            if user and report["report"].language == user.language:
                return report
            # If user is not registered take the search profile language
            if report["report"].language == search_profile_language:
                sp_language_report = report
            # English if none of the previous are available
            if report["report"].language == Language.EN.value:
                english_report = report

        if sp_language_report:
            return sp_language_report
        elif english_report:
            return english_report
        else:
            # Return the first report as last choice
            return reports[0] if reports else None

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
            pdf_as_link = search_profile.organization.pdf_as_link
            try:
                for email in search_profile.organization_emails:
                    user = await UserService.get_by_email(email)
                    report_in_user_lang = (
                        EmailService._get_report_in_user_language(
                            reports, user, search_profile.language
                        )
                    )
                    report = report_in_user_lang["report"]
                    presigned_url = report_in_user_lang["presigned_url"]
                    dashboard_url = report_in_user_lang["dashboard_url"]

                    if user and user.language in Language._value2member_map_:
                        translator_language = user.language
                    else:
                        translator_language = search_profile.language

                    translator = ArticleTranslationService.get_translator(
                        translator_language
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
                            user.last_name if user else None,
                            user.gender if user else None,
                            translator_language,
                            pdf_as_link,
                        ),
                        report_id=report.id,
                    )

                    await EmailService.schedule_email(email_schedule)
                    await EmailService.send_scheduled_emails()
                logger.info(
                    f"Email scheduling done for report {search_profile.name}"
                )
            except Exception as e:
                logger.error(f"Error in EmailService: {str(e)}")
                continue
