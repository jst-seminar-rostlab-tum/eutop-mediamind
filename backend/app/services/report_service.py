import uuid
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.core.config import configs
from app.core.logger import get_logger
from app.models.report import Report, ReportStatus
from app.repositories.report_repository import ReportRepository
from app.schemas.report_schemas import ReportCreate
from app.services.pdf_service import PDFService
from app.services.s3_service import S3Service
from app.services.search_profiles_service import SearchProfileService

logger = get_logger(__name__)


class ReportService:

    @staticmethod
    async def get_or_create_report(
        search_profile_id: uuid.UUID, timeslot: str
    ) -> Optional[Report]:
        """
        Fetches today's report for a given search profile an timeslot.
        If no report exists, generates a new one and stores it in S3.
        New reports are always generated for the current day.
        """
        # Try to find existing report
        report = await ReportRepository.get_by_search_profile_and_timeslot(
            search_profile_id, timeslot
        )
        if report:
            return report

        # Otherwise, create it
        logger.info(
            f"Generating {timeslot} report for profile {search_profile_id}"
        )
        return await ReportService._generate_and_store_report(
            search_profile_id, timeslot
        )

    @staticmethod
    async def _generate_and_store_report(
        search_profile_id: uuid.UUID, timeslot: str
    ) -> Optional[Report]:
        # Fetch search profile
        search_profile = await SearchProfileService.get_by_id(
            search_profile_id
        )
        if not search_profile:
            return None

        now = datetime.now()

        # Create a report entry first to get the report id
        temp_report_data = ReportCreate(
            search_profile_id=search_profile_id,
            created_at=now,
            time_slot=timeslot,
            s3_key="",  # set after upload
        )
        report = Report.model_validate(temp_report_data, from_attributes=True)
        report = await ReportRepository.create(report)

        # TODO: Replace with actual PDF generation logic
        pdf_bytes = await PDFService.create_sample_pdf(search_profile)

        # Set S3 key to the report id and upload the PDF
        s3_key = f"{configs.ENVIRONMENT}/reports/{search_profile_id}/{report.id}.pdf"  # noqa: E501
        await S3Service.upload_fileobj(file_bytes=pdf_bytes, key=s3_key)

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
