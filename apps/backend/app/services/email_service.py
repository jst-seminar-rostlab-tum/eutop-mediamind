import os
from dataclasses import dataclass
from datetime import datetime, timezone
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import gmtime, strftime
from typing import List
from uuid import UUID

from aiosmtplib import SMTP, SMTPResponseException
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import get_configs
from app.core.languages import Language
from app.core.logger import get_logger
from app.models.breaking_news import BreakingNews
from app.models.email import Email, EmailState
from app.models.user import Gender
from app.repositories.email_repository import EmailRepository
from app.repositories.organization_repository import OrganizationRepository
from app.services.s3_service import get_s3_service
from app.services.translation_service import ArticleTranslationService
from app.services.user_service import UserService

configs = get_configs()
logger = get_logger(__name__)

templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
templates_env = Environment(
    loader=FileSystemLoader(templates_dir),
    autoescape=select_autoescape(["html"]),
)


@dataclass
class EmailServer:
    hostname: str
    sender: str
    port: int
    use_tls: bool
    user: str
    password: str


@dataclass
class EmailSchedule:
    recipient: str
    subject: str
    content: str
    content_type: str
    report_id: UUID | None = None


class EmailService:

    @staticmethod
    def create_email(
        recipient: str,
        subject: str,
        content_type: str,
        content: str,
        report_id: UUID | None = None,
    ) -> Email:
        email = Email(
            sender=configs.SMTP_FROM,
            recipient=recipient,
            subject=subject,
            content_type=content_type,
            content=content,
            report_id=report_id,
        )
        return email

    @staticmethod
    def create_ses_email_server() -> EmailServer:
        return EmailServer(
            hostname=configs.SMTP_SERVER,
            port=configs.SMTP_PORT,
            use_tls=True,
            user=configs.SMTP_USER,
            password=configs.SMTP_PASSWORD,
            sender=configs.SMTP_FROM,
        )

    @staticmethod
    async def schedule_email(schedule: EmailSchedule) -> Email:
        email = EmailService.create_email(
            recipient=schedule.recipient,
            subject=schedule.subject,
            content_type=schedule.content_type,
            content=schedule.content,
            report_id=schedule.report_id,
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
                pdf_bytes = (
                    await s3_service.download_fileobj(email.report.s3_key)
                    if not pdf_as_link and email.report.s3_key
                    else None
                )
                await EmailService.send_email(email, pdf_bytes)
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
                    f"Failed to send email with id={email.id} to "
                    f"recipient {email.recipient}: {str(e)}"
                )

    @staticmethod
    async def send_email(
        email: Email,
        pdf_bytes: bytes | None = None,
    ) -> None:
        """
        Create email message, load attachments if any,
        and send email using SMTP.
        """
        msg = MIMEMultipart("alternative")
        msg["From"] = email.sender
        msg["To"] = email.recipient
        msg["Subject"] = email.subject

        html = MIMEText(email.content, "html")
        msg.attach(html)

        if pdf_bytes:
            attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
            attachment.add_header(
                "Content-Disposition", "attachment", filename="report.pdf"
            )
            msg.attach(attachment)

        await EmailService.__send_email(email=email, message=msg)

    @staticmethod
    async def __send_email(
        email: Email,
        message: MIMEMultipart,
    ) -> None:
        email_server = EmailService.create_ses_email_server()
        smtp_client = SMTP(
            hostname=email_server.hostname,
            port=email_server.port,
            use_tls=email_server.use_tls,
            timeout=60,  # seconds
        )
        try:
            await smtp_client.connect()
            await smtp_client.login(email_server.user, email_server.password)
        except Exception as e:
            error_message = f"Failed to connect to SMTP server: {str(e)}"
            logger.error(error_message)
            raise Exception(error_message)
        try:
            sendmail_response = await smtp_client.sendmail(
                email_server.sender, [email.recipient], message.as_string()
            )
        except SMTPResponseException as e:
            error_message = (
                f"Failed to send email with id={email.id} to "
                f"recipient={str([email.recipient])} with error: {str(e)}"
            )
            logger.error(error_message)
            raise Exception(error_message)
        finally:
            await smtp_client.quit()
        if not (
            isinstance(sendmail_response, tuple)
            and sendmail_response[1].startswith("Ok")
        ):
            raise Exception(
                f"Error sending emails for recipient={str(email.recipient)}: "
                f"{sendmail_response}"
            )

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
            salutation = f"{greeting} {title} {last_name}"
        else:
            salutation = f"{greeting}"

        context = {
            "s3_link": s3_link,
            "dashboard_link": dashboard_link,
            "profile_name": profile_name,
            "date": today,
            "language_code": language,
            "title": translator("Current Press Report"),
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
                "We have attached your PDF report to this "
                "email for your convenience"
            ),
            "click_text": translator("click here"),
            "text_4": translator(
                "If the link above does not work, copy and paste this URL "
                "into your browser"
            ),
            "deliver_text": translator("Delivered by MediaMind"),
            "disclaimer_text": EmailService.get_disclaimer_text(language),
            "pdf_as_link": pdf_as_link,
            "empty_pdf_text": translator(
                "There are no news items that match your "
                "search profile this time. We will notify you as soon as "
                "relevant news are found for your search profile"
            ),
        }

        template_name = "email_template.html"

        return EmailService._render_email_template(template_name, context)

    @staticmethod
    def _build_breaking_news_email_content(
        news: BreakingNews, language: str = Language.EN.value
    ) -> str:
        translator = ArticleTranslationService.get_translator(language)

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
            "disclaimer_text": EmailService.get_disclaimer_text(language),
            "title_big": translator("BREAKING NEWS ALERT"),
            "title": translator("Breaking News Alert"),
            "Published": translator("Published"),
            "read_full": translator("Read Full Article"),
            "text_1": translator(
                "If the button above does not work, copy and paste this URL "
                "into your browser"
            ),
            "deliver_text": translator("Delivered by MediaMind"),
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
            # Internal and external emails
            all_emails = (
                search_profile.organization_emails
                + search_profile.profile_emails
            )
            try:
                for email in all_emails:
                    user = await UserService.get_by_email(email)
                    report_in_user_lang = (
                        EmailService._get_report_in_user_language(
                            reports, user, search_profile.language
                        )
                    )
                    report = report_in_user_lang["report"]
                    presigned_url = report_in_user_lang["presigned_url"]
                    if email in search_profile.organization_emails:
                        dashboard_url = report_in_user_lang["dashboard_url"]
                    else:
                        dashboard_url = None

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
                        f"[MEDIAMIND] {translator('Your')} "
                        f"{time_slot_translated} {translator('Report')} "
                        f"{translator('for')} {search_profile.name}"
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

    @staticmethod
    def get_disclaimer_text(language: str = Language.EN.value) -> str:
        translator = ArticleTranslationService.get_translator(language)
        disclaimer_text = translator(
            "Replies to this email are handled by an AI assistant. You can "
            "reply with questions, but please avoid sharing personal or "
            "sensitive information."
        )
        return disclaimer_text

    @staticmethod
    def get_disclaimer_html(language: str = Language.EN.value) -> str:
        disclaimer_text = EmailService.get_disclaimer_text(language)
        return f"""
        <div style="
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
            font-size: 0.85em;
            color: #6c757d;
            font-style: italic;
            line-height: 1.4;
        ">
            <p style="margin: 0;">{disclaimer_text}</p>
        </div>
        """
