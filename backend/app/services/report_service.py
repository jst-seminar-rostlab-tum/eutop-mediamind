import uuid
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import select

from app.core.db import async_session
from app.models.report import Report, ReportStatus
from app.schemas.report_schemas import ReportCreate
from app.services.pdf_service import PDFService
from app.services.s3_service import S3Service
from app.services.search_profiles_service import SearchProfileService


class ReportService:

    @staticmethod
    async def get_or_create_report(
        search_profile_id: uuid.UUID, timeslot: str
    ) -> Report:
        # Try to find existing report
        report = await ReportService.get_report_by_search_profile_and_timeslot(
            search_profile_id, timeslot
        )
        if report:
            return report
        # Otherwise, create it
        return await ReportService._generate_and_store_report(
            search_profile_id, timeslot
        )

    @staticmethod
    async def _generate_and_store_report(
        search_profile_id: uuid.UUID, timeslot: str
    ) -> Report:
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
        report = await ReportService._create_report(temp_report_data)

        # TODO: Replace with actual PDF generation logic
        pdf_bytes = await PDFService.create_sample_pdf(search_profile)

        # Set S3 key to the report id and upload the PDF
        s3_key = f"reports/{report.id}.pdf"
        await S3Service.upload_fileobj(pdf_bytes, "eutop-mediamind", s3_key)

        # Update the report with the correct s3_key and mark as uploaded
        report.s3_key = s3_key
        report.status = ReportStatus.UPLOADED
        await ReportService._update_report(report)

        return report

    @staticmethod
    async def get_reports_by_search_profile(
        search_profile_id: UUID,
    ) -> List[Report]:
        async with async_session() as session:
            result = await session.execute(
                select(Report).where(
                    Report.search_profile_id == search_profile_id
                )
            )
            return result.scalars().all()

    @staticmethod
    async def get_report_by_id(report_id: UUID) -> Optional[Report]:
        async with async_session() as session:
            result = await session.execute(
                select(Report).where(Report.id == report_id)
            )
            return result.scalars().first()

    @staticmethod
    async def get_report_by_search_profile_and_timeslot(
        search_profile_id: UUID, timeslot: str
    ) -> Optional[Report]:
        async with async_session() as session:
            result = await session.execute(
                select(Report).where(
                    Report.search_profile_id == search_profile_id,
                    Report.time_slot == timeslot,
                    Report.status == ReportStatus.UPLOADED,
                )
            )
            return result.scalars().first()

    @staticmethod
    async def _create_report(
        report_data: ReportCreate,
    ) -> Report:
        async with async_session() as session:
            report = Report.from_orm(report_data)
            session.add(report)
            await session.commit()
            await session.refresh(report)
            return report

    @staticmethod
    async def _update_report(report: Report) -> Report:
        async with async_session() as session:
            db_report = await session.get(Report, report.id)
            if not db_report:
                raise ValueError("Report not found")
            for field, value in report.model_dump().items():
                setattr(db_report, field, value)
            session.add(db_report)
            await session.commit()
            await session.refresh(db_report)
            return db_report
