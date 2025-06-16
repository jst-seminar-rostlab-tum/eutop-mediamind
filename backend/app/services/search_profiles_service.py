from datetime import datetime, timedelta, timezone
from typing import List
from uuid import UUID

from fastapi import HTTPException

from app.core.db import async_session
from app.models import SearchProfile, Topic, User
from app.repositories.match_repository import MatchRepository
from app.repositories.match_repositoy import (
    get_recent_match_count_by_profile_id,
)
from app.repositories.search_profile_repository import (
    create_profile_with_request,
    get_accessible_profile_by_id,
    get_accessible_profiles,
    update_profile_with_request,
)
from app.repositories.subscription_repository import (
    get_all_subscriptions_with_search_profile,
    set_subscriptions_for_profile,
)
from app.schemas.articles_schemas import (
    ArticleOverviewItem,
    ArticleOverviewResponse,
    MatchDetailResponse,
)
from app.schemas.match_schemas import MatchFeedbackRequest
from app.schemas.search_profile_schemas import (
    KeywordSuggestionResponse,
    SearchProfileCreateRequest,
    SearchProfileDetailResponse,
    SearchProfileUpdateRequest,
)
from app.schemas.subscription_schemas import (
    SetSearchProfileSubscriptionsRequest,
    SubscriptionSummary,
)
from app.schemas.topic_schemas import TopicResponse
from app.services.llm_service.llm_client import LLMClient
from app.services.llm_service.llm_models import LLMModels


class SearchProfileService:
    @staticmethod
    async def create_search_profile(
        data: SearchProfileCreateRequest, current_user: User
    ) -> SearchProfileDetailResponse:
        async with async_session() as session:
            profile = await create_profile_with_request(
                data, current_user, session
            )
            return await SearchProfileService._build_profile_response(
                profile, current_user
            )

    @staticmethod
    async def get_search_profile_by_id(
        search_profile_id: UUID, current_user: User
    ) -> SearchProfileDetailResponse | None:
        async with async_session() as session:
            profile = await get_accessible_profile_by_id(
                search_profile_id=search_profile_id,
                user_id=current_user.id,
                organization_id=current_user.organization_id,
                session=session,
            )

            if profile is None:
                return None

            return await SearchProfileService._build_profile_response(
                profile, current_user
            )

    @staticmethod
    async def get_available_search_profiles(
        current_user: User,
    ) -> list[SearchProfileDetailResponse]:
        accessible_profiles = await get_accessible_profiles(
            current_user.id, current_user.organization_id
        )

        return [
            await SearchProfileService._build_profile_response(
                profile, current_user
            )
            for profile in accessible_profiles
        ]

    @staticmethod
    async def _build_profile_response(
        profile: SearchProfile, current_user: User
    ) -> SearchProfileDetailResponse:
        is_owner = profile.created_by_id == current_user.id
        is_editable = (
            is_owner
            or current_user.is_superuser
            or (
                profile.is_public
                and current_user.organization_id == profile.organization_id
            )
        )

        organization_emails = (
            profile.organization_emails
            if profile.organization_emails is not None
            else []
        )
        profile_emails = (
            profile.profile_emails
            if profile.profile_emails is not None
            else []
        )
        topic_responses = [
            SearchProfileService._build_topic_response(t)
            for t in profile.topics
        ]

        subscriptions = await get_all_subscriptions_with_search_profile(
            profile.id
        )

        time_threshold = datetime.now(timezone.utc) - timedelta(hours=24)
        new_articles_count = await get_recent_match_count_by_profile_id(
            profile.id, time_threshold
        )

        return SearchProfileDetailResponse(
            id=profile.id,
            name=profile.name,
            is_public=profile.is_public,
            editable=is_editable,
            is_editable=is_editable,
            owner_id=profile.created_by_id,
            is_owner=is_owner,
            organization_emails=organization_emails,
            profile_emails=profile_emails,
            topics=topic_responses,
            subscriptions=subscriptions,
            new_articles_count=new_articles_count,
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
        async with async_session() as session:
            db_profile = await get_accessible_profile_by_id(
                search_profile_id=search_profile_id,
                user_id=current_user.id,
                organization_id=current_user.organization_id,
                session=session,
            )

            if not db_profile:
                raise HTTPException(
                    status_code=404, detail="Profile not found"
                )

            if not (
                current_user.is_superuser
                or db_profile.created_by_id == current_user.id
                or (
                    db_profile.is_public
                    and db_profile.organization_id
                    == current_user.organization_id
                )
            ):
                raise HTTPException(
                    status_code=403, detail="Not allowed to edit this profile"
                )

            await update_profile_with_request(
                profile=db_profile,
                user=current_user,
                update_data=update_data,
                session=session,
            )

            return await SearchProfileService._build_profile_response(
                db_profile, current_user
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
            search_profile_id=search_profile_id, articles=articles
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
        a = match.article
        return MatchDetailResponse(
            match_id=match.id,
            comment=match.comment,
            sorting_order=match.sorting_order,
            article_id=a.id,
            title=a.title,
            url=a.url,
            author=a.author,
            published_at=a.published_at,
            language=a.language,
            category=a.category,
            summary=a.summary,
        )

    @staticmethod
    async def update_match_feedback(
        search_profile_id: UUID, match_id: UUID, data: MatchFeedbackRequest
    ) -> bool:
        match = await MatchRepository.update_match_feedback(
            search_profile_id,
            match_id,
            comment=data.comment,
            reason=data.reason,
            ranking=data.ranking,
        )
        return match is not None

    @staticmethod
    async def get_all_subscriptions_for_profile(
        search_profile_id: UUID,
    ) -> list[SubscriptionSummary]:
        return await get_all_subscriptions_with_search_profile(
            search_profile_id
        )

    @staticmethod
    async def set_search_profile_subscriptions(
        request: SetSearchProfileSubscriptionsRequest,
    ) -> None:
        await set_subscriptions_for_profile(
            profile_id=request.search_profile_id,
            subscription_ids=request.subscriptions,
        )

    @staticmethod
    async def get_keyword_suggestions(
        user: User, suggestions: List[str]
    ) -> KeywordSuggestionResponse:
        # Avoid useless LLM calls if no topics are available
        if len(suggestions) == 0:
            return KeywordSuggestionResponse(suggestions=[])

        prompt = """
        I will give you a list related keywords. Please add 5
        new relevant keywords. Don't include synonyms, but suggest
        words to pin down the topic more exactly with your added
        relevant keywords.\n
        """

        prompt += "Keywords: " + ", ".join(suggestions) + "\n\n"

        lhm_client = LLMClient(LLMModels.openai_4o)

        response = lhm_client.generate_typed_response(
            prompt, KeywordSuggestionResponse
        )
        if not response:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate keyword suggestions from LLM",
            )

        return response
