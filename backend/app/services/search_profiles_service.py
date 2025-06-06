from fastapi import HTTPException
from sqlalchemy import UUID

from app.core.db import async_session
from app.models import SearchProfile, Topic, User
from app.repositories.match_repository import MatchRepository
from app.repositories.search_profile_repository import (
    get_accessible_profiles,
    get_search_profile_by_id,
    update_profile_with_request, create_profile_with_request,
)
from app.repositories.topics_repository import TopicsRepository
from app.schemas.articles_schemas import (
    ArticleOverviewItem,
    ArticleOverviewResponse,
    MatchDetailResponse,
)
from app.schemas.match_schemas import MatchFeedbackRequest
from app.schemas.search_profile_schemas import (
    SearchProfileCreateRequest,
    SearchProfileDetailResponse,
    SearchProfileUpdateRequest,
)
from app.schemas.topic_schemas import TopicResponse


class SearchProfileService:
    @staticmethod
    async def create_search_profile(
            data: SearchProfileCreateRequest,
            current_user: User,
    ) -> SearchProfileDetailResponse:
        async with async_session() as session:
            profile = await create_profile_with_request(data, current_user, session)

        return SearchProfileService._build_profile_response(profile, current_user)

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
            id=topic.id,
            name=topic.name,
            keywords=[kw.name for kw in topic.keywords],
        )

    @staticmethod
    async def update_search_profile(
        search_profile_id: UUID,
        update_data: SearchProfileUpdateRequest,
        current_user: User,
    ) -> SearchProfileDetailResponse:
        profile = await get_search_profile_by_id(
            search_profile_id, current_user
        )
        if profile is None:
            raise HTTPException(status_code=404, detail="Profile not found")

        if (
            profile.created_by_id != current_user.id
            and not current_user.is_superuser
        ):
            raise HTTPException(
                status_code=403, detail="Not allowed to edit this profile"
            )

        async with async_session() as session:
            await update_profile_with_request(profile, update_data, session)

        return SearchProfileService._build_profile_response(
            profile, current_user
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
