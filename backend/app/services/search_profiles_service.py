from uuid import UUID

from app.models import SearchProfile
from app.repositories.match_repository import MatchRepository
from app.repositories.search_profile_repository import SearchProfileRepository
from app.schemas.articles_schemas import (
    ArticleOverviewItem,
    ArticleOverviewResponse,
    MatchDetailResponse,
)
from app.schemas.match_schemas import MatchFeedbackRequest
from app.schemas.search_profile_schemas import SearchProfileUpdateRequest


class SearchProfiles:

    @staticmethod
    async def get_search_profile(
        search_profile_id: UUID, current_user
    ) -> SearchProfile | None:
        return await SearchProfileRepository.get_by_id(
            search_profile_id, current_user
        )

    @staticmethod
    async def get_available_search_profiles(
        current_user,
    ) -> list[SearchProfile]:
        profiles = await SearchProfileRepository.get_accessible_profiles(
            current_user["id"], current_user["organization_id"]
        )
        return profiles

    @staticmethod
    async def update_search_profile(
        profile_id: UUID,
        data: SearchProfileUpdateRequest,
        current_user: dict,
    ) -> dict | None:
        profile = await SearchProfileRepository.get_by_id(profile_id)

        if not profile:
            return None

        # Check write rights
        is_owner = profile.created_by_id == current_user["id"]
        is_editable = data.is_editable or is_owner
        if not is_editable:
            return None

        updated = await SearchProfileRepository.update_by_id(profile_id, data)

        return updated

    @staticmethod
    async def get_article_overview(
        profile_id: UUID,
    ) -> ArticleOverviewResponse:
        matches = await MatchRepository.get_articles_by_profile(profile_id)

        articles = [
            ArticleOverviewItem.from_entity(m) for m in matches if m.article
        ]

        return ArticleOverviewResponse(
            search_profile_id=profile_id,
            articles=articles,
        )

    @staticmethod
    async def get_match_detail(
        profile_id: UUID, match_id: UUID
    ) -> MatchDetailResponse | None:
        match = await MatchRepository.get_match_by_id(profile_id, match_id)
        if not match or not match.article:
            return None

        article = match.article

        return MatchDetailResponse(
            match_id=match.id,
            comment=match.comment,
            sorting_order=match.sorting_order,
            article_id=article.id,
            title=article.title,
            url=article.url,
            author=article.author,
            published_at=article.published_at,
            language=article.language,
            category=article.category,
            summary=article.summary,
        )

    @staticmethod
    async def update_match_feedback(
        profile_id: UUID,
        match_id: UUID,
        data: MatchFeedbackRequest,
    ) -> bool:
        match = await MatchRepository.update_match_feedback(
            profile_id,
            match_id,
            comment=data.comment,
            reason=data.reason,
            ranking=data.ranking,
        )
        return match is not None
