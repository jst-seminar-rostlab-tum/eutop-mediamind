import logging
import uuid
from typing import Sequence

from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.core.db import async_session
from app.models import (
    ArticleKeywordLink,
    Match,
    SearchProfile,
    Topic,
)
from app.repositories.search_profile_repository import SearchProfileRepository

logger = logging.getLogger(__name__)


class ArticleMatchingService:
    """Service for matching articles to search profiles without subscription filtering."""

    @staticmethod
    async def match_article_to_search_profile(profile_id: uuid.UUID) -> None:
        """Load a profile (with topics→keywords), score its articles, and upsert Matches."""
        async with async_session() as session:
            # 1) Fetch the profile with topics→keywords all at once
            result = await session.execute(
                select(SearchProfile)
                .options(
                    selectinload(SearchProfile.topics).selectinload(
                        Topic.keywords
                    ),
                )
                .filter_by(id=profile_id)
            )
            sp: SearchProfile = result.scalars().one()

            # 2) Collect all keyword IDs to match on
            keyword_ids = [
                kw.id for topic in sp.topics for kw in topic.keywords
            ]
            if not keyword_ids:
                return

            # 3) Fetch all ArticleKeywordLinks for those keywords
            rows = await session.execute(
                select(
                    ArticleKeywordLink.article_id,
                    ArticleKeywordLink.score,
                ).where(ArticleKeywordLink.keyword_id.in_(keyword_ids))
            )

            # 4) Aggregate a score per article
            article_scores: dict[uuid.UUID, float] = {}
            for article_id, score in rows:
                article_scores.setdefault(article_id, 0.0)
                article_scores[article_id] += score

            logger.info(f"Calculated article scores: {article_scores}")

            if not article_scores:
                return

            # 5) Delete old matches for this profile
            await session.execute(
                delete(Match).where(Match.search_profile_id == profile_id)
            )

            # 6) Insert fresh matches in descending score order
            for order, (article_id, _) in enumerate(
                sorted(
                    article_scores.items(), key=lambda kv: kv[1], reverse=True
                )
            ):
                session.add(
                    Match(
                        article_id=article_id,
                        search_profile_id=profile_id,
                        sorting_order=order,
                        comment=None,
                    )
                )

            await session.commit()

    @staticmethod
    async def run(page_size: int = 100) -> None:
        """Page through all search profiles and run the matcher, logging but not re-raising errors."""
        page = 0
        while True:
            profiles: Sequence[SearchProfile] = (
                await SearchProfileRepository.fetch_all_search_profiles(
                    limit=page_size, offset=page * page_size
                )
            )
            logger.info(
                f"Processing profiles {page * page_size}–{(page + 1) * page_size}, count={len(profiles)}"
            )

            if not profiles:
                break

            for sp in profiles:
                logger.info(
                    f"Processing SearchProfile {sp.id} ({getattr(sp, 'name', '')})"
                )
                try:
                    await ArticleMatchingService.match_article_to_search_profile(
                        sp.id
                    )
                except Exception:
                    logger.exception(
                        "Error matching articles for SearchProfile %s", sp.id
                    )
                    # do not re-raise—just log and continue

            page += 1
