import os
from datetime import datetime

from apps.backend.app.core.logger import get_logger
from apps.backend.app.models.email import Email
from apps.backend.app.repositories.user_repository import UserRepository
from apps.backend.app.services.crawl_stats_pdf_service import (
    generate_crawl_stats_pdf,
)
from apps.backend.app.services.email_service import EmailService
from app.core.languages import Language

from app.core.config import get_configs

configs = get_configs()
logger = get_logger(__name__)


class AdminReportService:

    async def _generate_and_store_admin_report(self) -> str:

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"admin_report_{timestamp}.pdf"
        try:
            await generate_crawl_stats_pdf(report_filename)
            return report_filename

        except Exception as e:
            logger.error(f"Failed to generate admin report: {str(e)}")
            raise

    async def _send_admin_report_to_all_superusers(self, report_filename: str):
        superusers = await UserRepository.get_all_superusers()
        if not superusers:
            logger.warning("No superusers found to send the report.")
            return

        with open(report_filename, "rb") as f:
            pdf_bytes = f.read()

        if superuser and superuser.language in Language._value2member_map_:
            translator_language = superuser.language
        else:
            translator_language = Language.EN

        content = EmailService._build_admin_report_email_content(
            superuser.last_name if superuser else None,
            superuser.gender if superuser else None,
            translator_language
        )

        for superuser in superusers:
            if not superuser.email:
                logger.warning(f"Superuser {superuser.id} has no email address, skipping.")
                continue
                
            email = Email(
                sender=configs.SMTP_USER,
                recipient=superuser.email,
                subject="Admin Report",
                content=content,
            )

            await EmailService.send_ses_email(email, pdf_bytes)

    async def _delete_old_report(self, report_filename: str):
        try:
            if os.path.exists(report_filename):
                os.remove(report_filename)
                logger.info(f"Deleted old report: {report_filename}")
            else:
                logger.warning(
                    f"Report file not found for deletion: {report_filename}"
                )
        except Exception as e:
            logger.error(
                f"Failed to delete report file {report_filename}: {str(e)}"
            )
            raise

    async def run(self):
        report_filename = await self._generate_and_store_admin_report()
        await self._send_admin_report_to_all_superusers(report_filename)
        await self._delete_old_report(report_filename)
