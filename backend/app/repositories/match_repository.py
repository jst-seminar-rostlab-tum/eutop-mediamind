from uuid import UUID

from sqlalchemy.ext.asyncio import async_session
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.match import Match


class MatchRepository:
    @staticmethod
    async def get_articles_by_profile(profile_id: UUID) -> list[Match] | None:
        async with async_session() as session:
            result = await session.execute(
                select(Match)
                .options(selectinload(Match.article))
                .where(Match.search_profile_id == profile_id)
                .order_by(Match.sorting_order.asc())
            )
            return result.scalars().all()

    @staticmethod
    async def get_match_by_id(profile_id: UUID, match_id: UUID) -> Match | None:
        async with async_session() as session:
            result = await session.execute(
                select(Match)
                .options(selectinload(Match.article))
                .where(
                    Match.id == match_id,
                    Match.search_profile_id == profile_id,
                )
            )
            return result.scalars().first()
