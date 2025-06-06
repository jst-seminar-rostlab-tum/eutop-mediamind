from datetime import datetime
from uuid import UUID

from sqlmodel import func, select

from app.core.db import async_session
from app.models.article import Article
from app.models.match import Match


async def get_recent_match_counts_by_profile_ids(
    profile_ids: list[UUID],
    since: datetime,
) -> dict[UUID, int]:
    if not profile_ids:
        return {}

    async with async_session() as session:
        stmt = (
            select(Match.search_profile_id, func.count().label("count"))
            .join(Article, Match.article_id == Article.id)
            .where(
                Match.search_profile_id.in_(profile_ids),
                Article.published_at >= since,
            )
            .group_by(Match.search_profile_id)
        )
        result = await session.exec(stmt)
        return {row.search_profile_id: row.count for row in result.all()}
