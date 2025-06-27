from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import MatchingRun


class MatchingRunsRepository:
    """
    Repository for managing matching runs in the database.
    """

    @staticmethod
    async def create_matching_run(
        session: AsyncSession,
        algorithm_version: Optional[str] = None,
    ) -> MatchingRun:
        """
        Creates a new matching run.
        """
        matching_run = MatchingRun(algorithm_version=algorithm_version)
        session.add(matching_run)
        await session.commit()
        await session.refresh(matching_run)
        return matching_run
