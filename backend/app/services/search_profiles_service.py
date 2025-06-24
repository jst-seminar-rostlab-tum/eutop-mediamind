import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.db import async_session
from app.models import SearchProfile, Topic, User
from app.repositories.email_repository import EmailRepository
from app.models.associations import ArticleKeywordLink
from app.models.match import Match
from app.repositories.article_repository import ArticleRepository
from app.repositories.keyword_repository import KeywordRepository
from app.repositories.match_repository import MatchRepository
from app.repositories.search_profile_repository import SearchProfileRepository
from app.repositories.subscription_repository import (
    SubscriptionRepository,
)
from app.repositories.topics_repository import TopicsRepository
from app.schemas.articles_schemas import (
    ArticleOverviewResponse,
    MatchArticleOverviewContent,
    MatchDetailResponse,
    MatchItem,
    MatchProfileInfo,
    MatchTopicItem,
)
from app.schemas.match_schemas import MatchFeedbackRequest
from app.schemas.request_response import MatchFilterRequest
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
from app.schemas.user_schema import UserEntity
from app.services.article_vector_service import ArticleVectorService
from app.services.llm_service.llm_client import LLMClient
from app.services.llm_service.llm_models import LLMModels


class SearchProfileService:
    @staticmethod
    async def create_search_profile(
        data: SearchProfileCreateRequest,
        current_user: UserEntity,
    ) -> SearchProfileDetailResponse:
        """
        Create a new SearchProfile plus its topics, subscriptions and emails,
        then reload it with all relationships and return a detail response.
        """
        async with async_session() as session:
            async with session.begin():
                profile = SearchProfile(
                    name=data.name,
                    is_public=data.is_public,
                    organization_id=current_user.organization_id,
                    created_by_id=current_user.id,
                    owner_id=data.owner_id,
                )
                session.add(profile)
                await session.flush()  # ← now profile.id is assigned

                # sync the many‐to‐many/mapping tables
                await TopicsRepository.update_topics(
                    profile=profile,
                    new_topics=data.topics,
                    session=session,
                )
                await SubscriptionRepository.set_subscriptions_for_profile(
                    profile_id=profile.id,
                    subscriptions=data.subscriptions,
                    session=session,
                )
                await EmailRepository.update_emails(
                    profile_id=profile.id,
                    organization_emails=data.organization_emails or [],
                    profile_emails=data.profile_emails or [],
                    session=session,
                )

            result = await session.execute(
                select(SearchProfile)
                .where(SearchProfile.id == profile.id)
                .options(
                    # load related users if your detail schema includes them
                    selectinload(SearchProfile.users),
                    # load topics and, for each, its keywords
                    selectinload(SearchProfile.topics).selectinload(
                        Topic.keywords
                    ),
                )
            )
            fresh = result.scalar_one()

        return await SearchProfileService._build_profile_response(
            fresh, current_user
        )

    @staticmethod
    async def get_extended_by_id(
        search_profile_id: UUID, current_user: UserEntity
    ) -> SearchProfileDetailResponse | None:
        async with async_session() as session:
            profile = (
                await SearchProfileRepository.get_accessible_profile_by_id(
                    search_profile_id=search_profile_id,
                    user_id=current_user.id,
                    organization_id=current_user.organization_id,
                    session=session,
                )
            )

            if profile is None:
                return None

            return await SearchProfileService._build_profile_response(
                profile, current_user
            )

    @staticmethod
    async def get_by_id(search_profile_id: UUID) -> SearchProfile | None:
        return await SearchProfileRepository.get_by_id(search_profile_id)

    @staticmethod
    async def get_available_search_profiles(
        current_user: UserEntity,
    ) -> list[SearchProfileDetailResponse]:
        accessible_profiles = (
            await SearchProfileRepository.get_accessible_profiles(
                current_user.id, current_user.organization_id
            )
        )

        return [
            await SearchProfileService._build_profile_response(
                profile, current_user
            )
            for profile in accessible_profiles
        ]

    @staticmethod
    async def _build_profile_response(
        profile: SearchProfile, current_user: UserEntity
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

        subscriptions = await SubscriptionRepository.get_all_subscriptions_with_search_profile(  # noqa: E501
            profile.id
        )

        time_threshold = datetime.now(timezone.utc) - timedelta(hours=24)
        new_articles_count = (
            await (
                MatchRepository.get_recent_match_count_by_profile_id(
                    profile.id, time_threshold
                )
            )
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
        current_user: UserEntity,
    ) -> SearchProfileDetailResponse:
        async with async_session() as session:
            db_profile = (
                await SearchProfileRepository.get_accessible_profile_by_id(
                    search_profile_id=search_profile_id,
                    user_id=current_user.id,
                    organization_id=current_user.organization_id,
                    session=session,
                )
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

            await SearchProfileRepository.update_profile(
                profile=db_profile,
                data=update_data,
                session=session,
                current_user=current_user,
            )

            return await SearchProfileService._build_profile_response(
                db_profile, current_user
            )

    @staticmethod
    async def get_article_matches(
        search_profile_id: UUID,
        request: MatchFilterRequest,
        current_user: User,
    ) -> ArticleOverviewResponse:
        matches: list[Match] = []
        relevance_map: dict[UUID, float] = {}

        if request.searchTerm:
            # 1. Qdrant vertor search
            avs = ArticleVectorService()
            results = await avs.retrieve_by_similarity(
                query=request.searchTerm
            )

            # 2. extract article IDs and relevance scores
            article_ids = []
            for doc, score in results:
                aid = uuid.UUID(doc.metadata["id"])
                article_ids.append(aid)
                relevance_map[aid] = score

            # 3. get matches for the profile with the article IDs
            all_matches = await MatchRepository.get_articles_by_profile(
                search_profile_id
            )
            matches = [
                m
                for m in all_matches
                if m.article_id in article_ids
                and m.article
                and request.startDate
                <= m.article.published_at.date()
                <= request.endDate
            ]
        else:
            # no search term: get all matches for the profile
            matches = await MatchRepository.get_articles_by_profile(
                search_profile_id
            )
            matches = [
                m
                for m in matches
                if m.article
                and request.startDate
                <= m.article.published_at.date()
                <= request.endDate
            ]

        article_topic_scores: Dict[UUID, Dict[UUID, float]] = defaultdict(dict)
        article_topic_keywords: Dict[UUID, Dict[UUID, List[str]]] = (
            defaultdict(lambda: defaultdict(list))
        )
        topic_id_to_name: Dict[UUID, str] = {}
        topic_keywords: Dict[UUID, set] = {}
        keyword_links: List[ArticleKeywordLink] = []
        if request.subscriptions:
            matches = [
                m
                for m in matches
                if await ArticleRepository.get_subscription_id_for_article(
                    m.article_id
                )
                in request.subscriptions
            ]
            print(f"Filtered matches by subscriptions: {len(matches)} matches")
        async with async_session() as session:
            profile: SearchProfile = await SearchProfileRepository.get_accessible_profile_by_id(
                search_profile_id,
                user_id=current_user.id,
                organization_id=current_user.organization_id,
                session=session,
            )
        if request.topics:
            # gather keyword info to infer topic scores
            article_ids = [m.article_id for m in matches]
            keyword_links = await MatchRepository.get_keyword_links(
                article_ids
            )

            # build topic-keyword map
            topic_keywords: Dict[UUID, set] = {
                topic.id: {kw.id for kw in topic.keywords}
                for topic in profile.topics
            }

            all_keyword_ids = {link.keyword_id for link in keyword_links}
            all_keywords = await KeywordRepository.get_keywords_by_ids(
                list(all_keyword_ids)
            )
            keyword_id_to_name = {kw.id: kw.name for kw in all_keywords}

            article_topic_scores, article_topic_keywords = (
                SearchProfileService._compute_topic_scores(
                    keyword_links,
                    topic_keywords,
                    keyword_id_to_name,
                )
            )

        # sorting
        if request.sorting == "RELEVANCE" and request.searchTerm:
            matches.sort(
                key=lambda m: relevance_map.get(m.article_id, 0.0),
                reverse=True,
            )
        else:
            matches.sort(key=lambda m: m.article.published_at, reverse=True)

        topic_id_to_name = {t.id: t.name for t in profile.topics}

        # generate response
        match_items = [
            MatchItem.from_entity(
                m,
                relevance=relevance_map.get(m.article_id, 0.0),
                topic_scores=article_topic_scores.get(m.article_id, {}),
                topic_keywords=article_topic_keywords.get(m.article_id, {}),
                topic_id_to_name=topic_id_to_name,
            )
            for m in matches
        ]

        return ArticleOverviewResponse(matches=match_items)

    @staticmethod
    def _compute_topic_scores(
        keyword_links,
        topic_keywords: dict[UUID, set[UUID]],
        keyword_id_to_name: dict[UUID, str],
    ) -> tuple[
        dict[UUID, dict[UUID, float]], dict[UUID, dict[UUID, list[str]]]
    ]:
        score_sums = defaultdict(lambda: defaultdict(float))
        score_counts = defaultdict(lambda: defaultdict(int))
        keywords_map = defaultdict(lambda: defaultdict(list))

        for link in keyword_links:
            for topic_id, topic_kw_ids in topic_keywords.items():
                if link.keyword_id in topic_kw_ids:
                    score_sums[link.article_id][topic_id] += link.score
                    score_counts[link.article_id][topic_id] += 1
                    kw_name = keyword_id_to_name.get(link.keyword_id)
                    if kw_name:
                        keywords_map[link.article_id][topic_id].append(kw_name)

        topic_scores = defaultdict(dict)
        for article_id, topic_map in score_sums.items():
            for topic_id, total in topic_map.items():
                count = score_counts[article_id][topic_id]
                if count > 0:
                    topic_scores[article_id][topic_id] = total / count

        return topic_scores, keywords_map

    @staticmethod
    async def get_match_detail(
        search_profile_id: UUID, match_id: UUID, current_user: User
    ) -> MatchDetailResponse | None:
        match = await MatchRepository.get_match_by_id(
            search_profile_id, match_id
        )
        if not match or not match.article:
            return None
        a = match.article
        async with async_session() as session:
            profile = await SearchProfileRepository.get_accessible_profile_by_id(
                search_profile_id,
                user_id=current_user.id,
                organization_id=current_user.organization_id,
                session=session,
            )

        # get keyword links for the article
        keyword_links = await MatchRepository.get_keyword_links([a.id])
        topic_keywords = {
            topic.id: {kw.id for kw in topic.keywords}
            for topic in profile.topics
        }

        # load all keywords by their IDs
        all_keyword_ids = {link.keyword_id for link in keyword_links}
        all_keywords = await KeywordRepository.get_keywords_by_ids(
            list(all_keyword_ids)
        )
        keyword_id_to_name = {kw.id: kw.name for kw in all_keywords}

        # calculate topic scores and keywords
        topic_scores, topic_keyword_map = (
            SearchProfileService._compute_topic_scores(
                keyword_links, topic_keywords, keyword_id_to_name
            )
        )

        # build the response
        topics = []
        for t in profile.topics:
            score = topic_scores.get(a.id, {}).get(t.id)
            if score is None:
                continue
            topics.append(
                MatchTopicItem(
                    id=t.id,
                    name=t.name,
                    score=round(score, 4),
                    keywords=topic_keyword_map.get(a.id, {}).get(t.id, []),
                )
            )
        return MatchDetailResponse(
            match_id=match.id,
            topics=topics,
            search_profile=MatchProfileInfo(id=profile.id, name=profile.name),
            article=MatchArticleOverviewContent(
                headline={"de": a.title or "", "en": a.title or ""},
                summary={"de": a.summary or "", "en": ""},
                text={"de": a.content or "", "en": ""},
                image_urls=["http"] or [],
                published=a.published_at,
                crawled=a.crawled_at,
                authors=a.authors or [],
                status=a.status,
                categories=a.categories or [],
                language=a.language,
                newspaper_id=a.subscription_id,
            ),
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
        return await SubscriptionRepository.get_all_subscriptions_with_search_profile(  # noqa: E501
            search_profile_id
        )

    @staticmethod
    async def set_search_profile_subscriptions(
        request: SetSearchProfileSubscriptionsRequest,
    ) -> None:
        async with async_session() as session:
            await SubscriptionRepository.set_subscriptions_for_profile(
                profile_id=request.search_profile_id,
                subscriptions=request.subscriptions,
                session=session,
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
