from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlmodel import func

from app.core.db import async_session
from app.models import Article
from app.models.match import Match


class MatchRepository:
    @staticmethod
    async def get_articles_by_profile(
        search_profile_id: UUID,
    ) -> List[Match] | None:
        async with async_session() as session:
            articles = await session.execute(
                select(Match)
                .options(
                    selectinload(Match.article), selectinload(Match.topic)
                )
                .where(Match.search_profile_id == search_profile_id)
                .order_by(Match.sorting_order.asc())
            )
            return articles.scalars().all()

    @staticmethod
    async def get_matches_by_search_profile(
        search_profile_id: UUID,
    ) -> List[Match]:
        async with async_session() as session:
            query = (
                select(Match)
                .options(selectinload(Match.article))
                .where(Match.search_profile_id == search_profile_id)
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
    async def get_matches_by_profile_and_article(
        search_profile_id: UUID,
        article_id: UUID,
    ) -> list[Match]:
        async with async_session() as session:
            result = await session.execute(
                select(Match)
                .where(
                    Match.search_profile_id == search_profile_id,
                    Match.article_id == article_id,
                )
                .options(
                    selectinload(Match.topic),
                )
            )
            return result.scalars().all()

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
    async def get_recent_match_count_by_profile_id(
        profile_id: UUID,
        since: datetime,
    ) -> int:
        async with async_session() as session:
            stmt = (
                select(func.count().label("count"))
                .select_from(Match)
                .join(Article, Match.article_id == Article.id)
                .where(
                    Match.search_profile_id == profile_id,
                    Article.published_at >= since,
                )
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none() or 0

    @staticmethod
    async def insert_match(match: Match, session) -> Match | None:
        """
        Insert a new Match into the database.
        """
        try:
            session.add(match)
            await session.commit()
            await session.refresh(match)
            return match
        except IntegrityError:
            await session.rollback()
            return None

    @staticmethod
    async def delete_for_search_profile(
        session: AsyncSession, profile_id: UUID
    ) -> None:
        stmt = delete(Match).where(Match.search_profile_id == profile_id)
        await session.execute(stmt)

    @staticmethod
    async def match_exists(
        session: AsyncSession,
        search_profile_id: UUID,
        article_id: UUID,
    ) -> bool:
        """
        Check if a match already exists
        for the given search_profile_id
        and article_id combination.
        """
        result = await session.execute(
            select(Match)
            .where(
                Match.search_profile_id == search_profile_id,
                Match.article_id == article_id,
            )
            .limit(1)
        )
        return result.scalars().first() is not None
