from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import MatchingRun


class MatchingRunRepository:
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

    @staticmethod
    async def get_last_matching_run(
        session: AsyncSession,
    ) -> Optional[MatchingRun]:
        """
        Queries the database and returns the most recent MatchingRun
        based on the 'created_at' field.

        :param session: AsyncSession to use for the query.
        :return: The latest MatchingRun or None if no entries exist.
        """
        statement = (
            select(MatchingRun)
            .order_by(MatchingRun.created_at.desc())
            .limit(1)
        )
        result = await session.execute(statement)
        return result.scalar().first()
