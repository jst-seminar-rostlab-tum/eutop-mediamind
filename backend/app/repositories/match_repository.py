from typing import List
from uuid import UUID

from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.db import async_session
from app.models import User
from app.models.match import Match


class MatchRepository:
    @staticmethod
    async def get_articles_by_profile(
        search_profile_id: UUID,
    ) -> List[Match] | None:
        async with async_session() as session:
            articles = await session.execute(
                select(Match)
                .options(selectinload(Match.article))
                .where(Match.search_profile_id == search_profile_id)
                .order_by(Match.sorting_order.asc())
            )
            return articles.scalars().all()

    @staticmethod
    async def get_matches_by_search_profile(
        search_profile_id: UUID, user: User
    ) -> List[Match]:
        async with async_session() as session:
            query = select(Match).where(
                Match.search_profile_id == search_profile_id
            )
            matches = (await session.execute(query)).scalars().all()

            return matches

    @staticmethod
    async def get_match_by_id(
        search_profile_id: UUID, match_id: UUID
    ) -> Match | None:
        async with async_session() as session:
            matches = await session.execute(
                select(Match)
                .options(selectinload(Match.article))
                .where(
                    Match.id == match_id,
                    Match.search_profile_id == search_profile_id,
                )
            )
            return matches.scalars().first()

    @staticmethod
    async def update_match_feedback(
        search_profile_id: UUID,
        match_id: UUID,
        comment: str,
        reason: str,
        ranking: int,
    ) -> Match | None:
        async with async_session() as session:
            match = await session.get(Match, match_id)
            if not match or match.search_profile_id != search_profile_id:
                return None

            match.comment = f"{comment} [reason: {reason}, ranking: {ranking}]"
            await session.commit()
            await session.refresh(match)
            return match
