import uuid
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from app.core.config import configs
from app.core.languages import Language
from app.core.logger import get_logger
from app.models.report import Report, ReportStatus
from app.repositories.report_repository import ReportRepository
from app.repositories.search_profile_repository import SearchProfileRepository
from app.schemas.report_schemas import ReportCreate
from app.services.pdf_service.pdf_service import PDFService
from app.services.s3_service import S3Service, get_s3_service
from app.services.search_profiles_service import SearchProfileService

logger = get_logger(__name__)


class ReportService:

    @staticmethod
    async def get_or_create_report(
        search_profile_id: uuid.UUID,
        timeslot: str,
        language: str,
        s3_service: S3Service,
    ) -> Optional[Report]:
        """
        Fetches today's report for a search profile, timeslot and language.
        If no report exists, generates a new one and stores it in S3.
        New reports are always generated for the current day.
        """

        # Try to find existing report
        report = await ReportRepository.get_by_searchprofile_timeslot_language(
            search_profile_id, timeslot, language
        )
        if report:
            return report

        # Otherwise, create it
        logger.info(
            f"Generating {timeslot} report ({language}) for profile {search_profile_id}"  # noqa: E501
        )

        return await ReportService._generate_and_store_report(
            search_profile_id, timeslot, language, s3_service
        )

    @staticmethod
    async def _generate_and_store_report(
        search_profile_id: uuid.UUID,
        timeslot: str,
        language: str,
        s3_service: S3Service,
    ) -> Optional[Report]:
        # Fetch search profile
        search_profile = await SearchProfileService.get_by_id(
            search_profile_id
        )
        if not search_profile:
            return None

        now = datetime.now(timezone.utc)

        # Create a report entry first to get the report id
        temp_report_data = ReportCreate(
            search_profile_id=search_profile_id,
            created_at=now,
            time_slot=timeslot,
            language=language,
            s3_key="",  # set after upload
        )
        report = Report.model_validate(temp_report_data, from_attributes=True)
        report = await ReportRepository.create(report)

        # PDF generation
        pdf_bytes = await PDFService.create_pdf(
            search_profile_id, timeslot, language, now
        )

        # Set S3 key to the report id and upload the PDF
        s3_key = f"{configs.ENVIRONMENT}/reports/{search_profile_id}/{report.id}.pdf"  # noqa: E501
        await s3_service.upload_fileobj(file_bytes=pdf_bytes, key=s3_key)

        # Update the report with the correct s3_key and mark as uploaded
        report.s3_key = s3_key
        report.status = ReportStatus.UPLOADED
        report = await ReportRepository.update(report)

        return report

    @staticmethod
    async def get_reports_by_search_profile(
        search_profile_id: UUID,
    ) -> List[Report]:
        return await ReportRepository.get_by_search_profile(search_profile_id)

    @staticmethod
    async def get_report_by_id(report_id: UUID) -> Optional[Report]:
        return await ReportRepository.get_by_id(report_id)

    @staticmethod
    async def run(
        timeslot: str,
        languages: List[Language],
    ):
        """
        Run the report generation process for a specific timeslot
        in the pipeline.
        """
        s3_service = get_s3_service()
        reports = []
        search_profiles = (
            await SearchProfileRepository.fetch_all_search_profiles()
        )
        for search_profile in search_profiles:
            for lang in languages:
                report = await ReportService.get_or_create_report(
                    search_profile.id, timeslot, lang.value, s3_service
                )

                # For email generation
                presigned_url = s3_service.generate_presigned_url(
                    key=report.s3_key, expires_in=604800  # 7 days
                )
                dashboard_url = (
                    "https://mediamind.csee.tech/dashboard/reports/"
                    f"{report.id}"
                )

                reports.append(
                    {
                        "report": report,
                        "presigned_url": presigned_url,
                        "dashboard_url": dashboard_url,
                        "search_profile": search_profile,
                    }
                )
        return reports
