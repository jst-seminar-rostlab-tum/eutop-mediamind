from datetime import datetime
from uuid import UUID

from sqlmodel import func, select

from app.core.db import async_session
from app.models.article import Article
from app.models.match import Match


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
