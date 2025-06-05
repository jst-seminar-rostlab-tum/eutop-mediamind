from uuid import UUID

from app.core.logger import get_logger
from app.models import SearchProfile, User
from app.models.search_profile import (
    SearchProfileCreate,
    SearchProfileRead,
    SearchProfileUpdate,
)
from app.repositories.match_repository import MatchRepository
from app.repositories.search_profile_repository import (
    get_available_search_profiles,
    get_search_profile_by_id,
    save_search_profile,
    save_updated_search_profile,
)
from app.schemas.articles_schemas import (
    ArticleOverviewItem,
    ArticleOverviewResponse,
    MatchDetailResponse,
)
from app.schemas.match_schemas import MatchFeedbackRequest
from app.schemas.search_profile_schemas import SearchProfileDetailResponse

logger = get_logger(__name__)


class SearchProfiles:
    @staticmethod
    async def create_search_profile(
        new_search_profile_data: SearchProfileCreate,
        current_user: User,
    ) -> SearchProfileRead:
        new_search_profile = SearchProfile(
            name=new_search_profile_data.name,
            organization_id=new_search_profile_data.organization_id,
            is_public=False,
            created_by_id=current_user.id,
        )
        saved_search_profile = await save_search_profile(new_search_profile)
        return SearchProfileRead.model_validate(saved_search_profile)

    @staticmethod
    async def get_search_profile_by_id(
        search_profile_id: UUID,
        current_user: User,
    ) -> SearchProfileDetailResponse | None:
        profiles = await SearchProfiles.get_available_search_profiles(
            current_user
        )
        return next((p for p in profiles if p.id == search_profile_id), None)

    @staticmethod
    async def get_available_search_profiles(
        current_user: User,
    ) -> list[SearchProfileDetailResponse]:
        profiles = await get_available_search_profiles(current_user)
        logger.info(profiles)
        return profiles

    @staticmethod
    async def update_search_profile(
        search_profile_id: UUID,
        update_data: SearchProfileUpdate,
        current_user: User,
    ) -> SearchProfileRead | None:
        # Load the raw SQLModel (not a response object)
        search_profile = await get_search_profile_by_id(
            search_profile_id, current_user
        )
        if search_profile is None:
            return None

        # Only allow owner or superuser to update
        if (
            search_profile.created_by_id != current_user.id
            and not current_user.is_superuser
        ):
            return None

        if update_data.name is not None:
            search_profile.name = update_data.name
        if update_data.description is not None:
            search_profile.description = update_data.description

        updated_profile = await save_updated_search_profile(search_profile)
        return SearchProfileRead.model_validate(updated_profile)

    @staticmethod
    async def get_article_overview(
        search_profile_id: UUID,
    ) -> ArticleOverviewResponse:
        matches = await MatchRepository.get_articles_by_profile(
            search_profile_id
        )

        articles = [
            ArticleOverviewItem.from_entity(m) for m in matches if m.article
        ]

        return ArticleOverviewResponse(
            search_profile_id=search_profile_id,
            articles=articles,
        )

    @staticmethod
    async def get_match_detail(
        search_profile_id: UUID, match_id: UUID
    ) -> MatchDetailResponse | None:
        match = await MatchRepository.get_match_by_id(
            search_profile_id, match_id
        )
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
        search_profile_id: UUID,
        match_id: UUID,
        data: MatchFeedbackRequest,
    ) -> bool:
        match = await MatchRepository.update_match_feedback(
            search_profile_id,
            match_id,
            comment=data.comment,
            reason=data.reason,
            ranking=data.ranking,
        )
        return match is not None
