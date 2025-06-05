from uuid import UUID

from fastapi import HTTPException
from winerror import ERROR_PROFILE_NOT_FOUND

from app.core.db import async_session
from app.core.logger import get_logger
from app.models import SearchProfile, Topic, User
from app.models.search_profile import (
    SearchProfileCreate,
    SearchProfileRead,
    SearchProfileUpdate,
)
from app.repositories.match_repository import MatchRepository
from app.repositories.search_profile_repository import (
    get_accessible_profiles,
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
from app.schemas.search_profile_schemas import (
    SearchProfileDetailResponse,
    SearchProfileUpdateRequest,
)
from app.schemas.topic_schemas import TopicResponse

logger = get_logger(__name__)


class SearchProfileService:
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
        profiles = await SearchProfileService.get_available_search_profiles(
            current_user
        )
        return next((p for p in profiles if p.id == search_profile_id), None)

    @staticmethod
    async def get_available_search_profiles(
        current_user: User,
    ) -> list[SearchProfileDetailResponse]:
        accessible_profiles = await get_accessible_profiles(
            current_user.id, current_user.organization_id
        )

        return [
            SearchProfileService._build_profile_response(profile, current_user)
            for profile in accessible_profiles
        ]

    @staticmethod
    def _build_profile_response(
        profile: SearchProfile, current_user: User
    ) -> SearchProfileDetailResponse:
        is_owner = profile.created_by_id == current_user.id
        is_editable = is_owner or current_user.is_superuser

        organization_emails = SearchProfileService._filter_emails_by_org(
            profile, current_user.organization_id, include=True
        )
        profile_emails = SearchProfileService._filter_emails_by_org(
            profile, current_user.organization_id, include=False
        )

        topic_responses = [
            SearchProfileService._build_topic_response(topic)
            for topic in profile.topics
        ]

        return SearchProfileDetailResponse(
            id=profile.id,
            name=profile.name,
            organization_emails=organization_emails,
            profile_emails=profile_emails,
            public=profile.is_public,
            editable=is_editable,
            is_editable=is_editable,
            owner=profile.created_by_id,
            is_owner=is_owner,
            topics=topic_responses,
        )

    @staticmethod
    def _filter_emails_by_org(
        profile: SearchProfile, org_id: UUID, include: bool
    ) -> list[str]:
        return [
            user.email
            for user in profile.users
            if (user.organization_id == org_id) is include
        ]

    @staticmethod
    def _build_topic_response(topic: Topic) -> TopicResponse:
        return TopicResponse(
            name=topic.name, keywords=[kw.name for kw in topic.keywords]
        )

    @staticmethod
    async def update_search_profile(
        search_profile_id: UUID,
        update_data: SearchProfileUpdate,
        current_user: User,
    ) -> SearchProfileRead | None:
        search_profile = await get_search_profile_by_id(
            search_profile_id, current_user
        )
        if search_profile is None:
            raise ERROR_PROFILE_NOT_FOUND("Search-profile not found")

        if (
            search_profile.created_by_id != current_user.id
            and not current_user.is_superuser
        ):
            raise ERROR_PROFILE_NOT_FOUND("Search-profile not found")

        # Perform partial update
        if update_data.name is not None:
            search_profile.name = update_data.name
        if update_data.description is not None:
            search_profile.description = update_data.description

        updated_profile = await save_updated_search_profile(search_profile)
        return SearchProfileRead.model_validate(updated_profile)

    @staticmethod
    async def update_full_profile(
        search_profile_id: UUID,
        update_data: SearchProfileUpdateRequest,
        current_user: User,
    ) -> SearchProfile | None:
        async with async_session() as session:
            search_profile = await session.get(
                SearchProfile, search_profile_id
            )
            if not search_profile:
                return None

            if (
                search_profile.created_by_id != current_user.id
                and not current_user.is_superuser
            ):
                raise HTTPException(status_code=403, detail="Forbidden")

            SearchProfileService._update_basic_fields(
                search_profile, update_data
            )
            SearchProfileService._update_optional_lists(
                search_profile, update_data
            )
            SearchProfileService._update_relationships(
                search_profile, update_data
            )

            session.add(search_profile)
            await session.commit()
            await session.refresh(search_profile)
            return search_profile

    @staticmethod
    def _update_basic_fields(
        search_profile: SearchProfile, data: SearchProfileUpdateRequest
    ) -> None:
        search_profile.name = data.name
        search_profile.is_public = data.public
        search_profile.is_editable = data.is_editable
        search_profile.owner_id = data.owner
        search_profile.is_owner = data.is_owner

    @staticmethod
    def _update_optional_lists(
        search_profile: SearchProfile, data: SearchProfileUpdateRequest
    ) -> None:
        if data.organization_emails is not None:
            search_profile.organization_emails = data.organization_emails

        if data.profile_emails is not None:
            search_profile.profile_emails = data.profile_emails

    @staticmethod
    def _update_relationships(
        search_profile: SearchProfile, data: SearchProfileUpdateRequest
    ) -> None:
        if data.subscriptions is not None:
            search_profile.subscriptions.clear()
            search_profile.subscriptions.extend(
                sub.to_model() for sub in data.subscriptions
            )

        if data.topics is not None:
            search_profile.topics.clear()
            search_profile.topics.extend(
                topic.to_model() for topic in data.topics
            )

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
