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

    @staticmethod
    async def add_match(match: Match):
        """
        Add a new Match entry or update an existing one
        with the same article_id, search_profile_id, and match_date.
        """
        async with async_session() as session:
            # 1. Look for an existing match
            stmt = select(Match).where(
                Match.article_id == match.article_id,
                Match.search_profile_id == match.search_profile_id,
                Match.match_date == match.match_date,
            )
            result = await session.execute(stmt)
            existing: Match | None = result.scalar_one_or_none()

            if existing:
                print(
                    f"Match with article_id {match.article_id} already exists. Updating existing entry."
                )
                # 2a. Update the existing entry
                existing.topic_id = match.topic_id
                existing.sorting_order = match.sorting_order
                existing.comment = match.comment

                session.add(existing)  # redundant but clarifies intent
                await session.commit()
                await session.refresh(existing)
                return existing
            else:
                # 2b. Insert a new entry
                session.add(match)
                await session.commit()
                await session.refresh(match)
                return match
