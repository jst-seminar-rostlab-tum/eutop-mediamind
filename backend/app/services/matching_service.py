import uuid
from typing import Sequence

from sqlalchemy import delete
from sqlmodel import select

from app.core.db import async_session
from app.models import ArticleKeywordLink, Match, SearchProfile
from app.repositories.search_profile_repository import SearchProfileRepository


class ArticleMatchingService:
    """Service for matching articles"""

    @staticmethod
    async def match_article_to_search_profile(
        search_profile: SearchProfile
    ) -> None:
        """Match articles to a given search profile."""
        async with async_session() as session:
            session.add(search_profile)
            await session.refresh(search_profile, ["topics", "subscriptions"])

            keyword_ids = [
                kw.id
                for topic in search_profile.topics
                for kw in topic.keywords
            ]
            if not keyword_ids:
                return

            query = select(ArticleKeywordLink).where(
                ArticleKeywordLink.keyword_id.in_(keyword_ids)
            )
            links: Sequence[ArticleKeywordLink] = (
                (await session.execute(query)).scalars().all()
            )

            subscription_ids = {sub.id for sub in search_profile.subscriptions}

            article_scores: dict[uuid.UUID, float] = {}

            for link in links:
                art = (
                    link.article
                )  # Relationship von ArticleKeywordLink auf Article
                if art.subscription_id in subscription_ids:
                    article_scores.setdefault(art.id, 0.0)
                    article_scores[art.id] += link.score

            if not article_scores:
                return

            await session.execute(
                delete(Match).where(
                    Match.search_profile_id == search_profile.id
                )
            )

            sorted_articles = sorted(
                article_scores.items(), key=lambda item: item[1], reverse=True
            )

            for order, (article_id, total_score) in enumerate(sorted_articles):
                match = Match(
                    article_id=article_id,
                    search_profile_id=search_profile.id,
                    sorting_order=order,
                    comment=None,  # optional befüllbar
                )
                session.add(match)

            await session.commit()


    @staticmethod
    async def run(self, page_size: int = 100) -> None:
        """Run the article matching process."""

        page: int = 0
        offset: int = page * page_size

        search_profiles: Sequence[SearchProfile] = (
            await SearchProfileRepository.fetch_all_search_profiles(
                limit=page_size, offset=offset
            )
        )

        while search_profiles:
            for search_profile in search_profiles:
                try:
                    await ArticleMatchingService.match_article_to_search_profile(search_profile)
                except Exception as e:
                    raise e

            page += 1
            offset = page * page_size

            search_profiles = (
                await SearchProfileRepository.fetch_all_search_profiles(
                    limit=page_size, offset=offset
                )
            )
