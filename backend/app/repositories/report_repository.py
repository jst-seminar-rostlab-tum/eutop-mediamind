from typing import List, Optional
from uuid import UUID

from sqlmodel import select

from app.core.db import async_session
from app.models.report import Report, ReportStatus


class ReportRepository:
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
    async def create_report(report: Report) -> Report:
        async with async_session() as session:
            session.add(report)
            await session.commit()
            await session.refresh(report)
            return report

    @staticmethod
    async def update_report(report: Report) -> Report:
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
