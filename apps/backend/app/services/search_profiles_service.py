# flake8: noqa: E501
import traceback
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import List
from uuid import UUID

from fastapi import HTTPException
from qdrant_client.common.client_exceptions import QdrantException
from qdrant_client.http.exceptions import UnexpectedResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.db import async_session
from app.core.languages import Language
from app.core.logger import get_logger
from app.models import SearchProfile, Topic
from app.models.match import Match
from app.models.user import UserRole
from app.repositories.article_repository import ArticleRepository
from app.repositories.email_repository import EmailRepository
from app.repositories.entity_repository import ArticleEntityRepository
from app.repositories.keyword_repository import KeywordRepository
from app.repositories.match_repository import MatchRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.search_profile_repository import SearchProfileRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.topics_repository import TopicsRepository
from app.repositories.user_repository import UserRepository
from app.schemas.articles_schemas import (
    ArticleOverviewResponse,
    MatchArticleOverviewContent,
    MatchDetailResponse,
    MatchItem,
    MatchProfileInfo,
    MatchTopicItem,
)
from app.schemas.match_schemas import MatchFeedbackRequest, MatchFilterRequest
from app.schemas.search_profile_schemas import (
    KeywordSuggestionResponse,
    KeywordSuggestionTopic,
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
from app.services.llm_service.llm_models import TaskModelMapping
from app.services.llm_service.prompts.keyword_suggestion_prompts import (
    KEYWORD_SUGGESTION_PROMPT_DE,
    KEYWORD_SUGGESTION_PROMPT_EN,
)

logger = get_logger(__name__)


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
                    language=data.language,
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
                await SearchProfileRepository.update_user_rights(
                    profile=profile,
                    can_read_user_ids=data.can_read_user_ids,
                    can_edit_user_ids=data.can_edit_user_ids,
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
                    user_role=current_user.role,
                    is_superuser=current_user.is_superuser,
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
    ) -> List[SearchProfileDetailResponse]:
        accessible_profiles = (
            await SearchProfileRepository.get_accessible_profiles(
                current_user.id,
                current_user.organization_id,
                current_user.role,
                current_user.is_superuser,
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
        is_owner = profile.owner_id == current_user.id

        is_editor = (
            current_user.id == profile.owner_id
            or current_user.is_superuser
            or current_user.id in profile.can_edit_user_ids
        )

        is_reader = (
            current_user.id == profile.owner_id
            or current_user.is_superuser
            or current_user.id in profile.can_read_user_ids
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
            owner_id=profile.owner_id,
            is_owner=is_owner,
            can_read_user_ids=profile.can_read_user_ids,
            is_reader=is_reader,
            can_edit_user_ids=profile.can_edit_user_ids,
            is_editor=is_editor,
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
                    user_role=current_user.role,
                    is_superuser=current_user.is_superuser,
                    organization_id=current_user.organization_id,
                    session=session,
                )
            )

            if not db_profile:
                raise HTTPException(
                    status_code=404, detail="Profile not found"
                )

            allow_edit = (
                current_user.is_superuser
                or db_profile.created_by_id == current_user.id
                or (
                    db_profile.organization_id == current_user.organization_id
                    and current_user.role == UserRole.maintainer
                )
                or (
                    db_profile.is_public
                    and db_profile.organization_id
                    == current_user.organization_id
                )
            )

            if not allow_edit:
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
    ) -> ArticleOverviewResponse:
        matches: List[Match] = []
        relevance_map: dict[UUID, float] = {}

        search_profile = await SearchProfileRepository.get_by_id(
            search_profile_id
        )

        if request.searchTerm:
            import re

            def split_words(text):
                if not text:
                    return []
                return re.findall(r"[\wäöüßÄÖÜ]+", text.lower())

            search_words = split_words(request.searchTerm)
            min_match = len(search_words)

            def field_match(field):
                combined_text = " ".join(fields).lower()
                combined_words = set(split_words(combined_text))
                return sum(
                    w in combined_words or w in combined_text
                    for w in search_words
                )

            all_matches = await MatchRepository.get_matches_by_search_profile(
                search_profile_id,
            )
            matches = []
            for m in all_matches:
                if not m.article:
                    continue
                fields = [
                    m.article.title_de or "",
                    m.article.title_en or "",
                    m.article.summary_de or "",
                    m.article.summary_en or "",
                ]
                found = False
                for field in fields:
                    if field:
                        match_count = field_match(field)
                        if match_count >= min_match:
                            found = True
                            break
                if (
                    found
                    and request.startDate
                    <= m.article.published_at.date()
                    <= request.endDate
                ):
                    matches.append(m)
        else:
            # no search term: get all matches for the profile
            matches = await MatchRepository.get_matches_by_search_profile(
                search_profile_id,
            )
            matches = [
                m
                for m in matches
                if m.article
                and request.startDate
                <= m.article.published_at.date()
                <= request.endDate
            ]

        if request.subscriptions:
            matches = [
                m
                for m in matches
                if await ArticleRepository.get_subscription_id_for_article(
                    m.article_id
                )
                in request.subscriptions
            ]

        # filter matches by requested topics
        if request.topics:
            requested_topic_ids = set(request.topics)
            matches = [m for m in matches if m.topic_id in requested_topic_ids]

        # sorting
        if request.sorting == "RELEVANCE":
            matches.sort(key=lambda m: m.score, reverse=True)
        else:
            matches.sort(key=lambda m: m.article.published_at, reverse=True)

        article_match_map: dict[UUID, List[Match]] = defaultdict(list)
        for m in matches:
            article_match_map[m.article_id].append(m)

        all_topic_ids = {m.topic_id for m in matches if m.topic_id is not None}

        topic_names = await TopicsRepository.get_topic_names_by_ids(
            all_topic_ids
        )
        topic_keywords_map = await KeywordRepository.get_keywords_by_topic_ids(
            all_topic_ids
        )

        match_items = []
        for article_id, match_group in article_match_map.items():
            topics_dict = {}
            total_score = 0.0
            article = match_group[0].article
            has_organization_subscription_access = await SubscriptionRepository.has_organization_subscription_access(
                search_profile.organization_id, article.subscription_id
            )

            for m in match_group:
                topic_id = m.topic_id
                if topic_id is None or topic_id in topics_dict:
                    continue

                topics_dict[topic_id] = MatchTopicItem(
                    id=topic_id,
                    name=topic_names.get(topic_id, ""),
                    score=round(m.score, 4),
                    keywords=topic_keywords_map.get(topic_id, []),
                )
                total_score += m.score

            topics = list(topics_dict.values())

            avg_score = total_score / len(topics) if topics else 0.0

            categories = (
                article.categories
                if isinstance(article.categories, list)
                else (
                    [article.categories]
                    if article.categories is not None
                    else []
                )
            )

            # Check if organization has subscription access and modify content accordingly
            if has_organization_subscription_access:
                article_text = {
                    "de": article.content_de or "",
                    "en": article.content_en or "",
                }
            else:
                article_text = {
                    "de": None,
                    "en": None,
                }

            article_content = MatchArticleOverviewContent(
                article_url=article.url or "",
                headline={
                    "de": article.title_de or "",
                    "en": article.title_en or "",
                },
                summary={
                    "de": article.summary_de or "",
                    "en": article.summary_en or "",
                },
                text=article_text,
                image_urls=[url for url in [article.image_url] if url],
                published=article.published_at,
                crawled=article.crawled_at,
                newspaper_id=article.subscription_id,
                authors=article.authors or [],
                categories=categories,
                status=article.status,
            )

            match_items.append(
                MatchItem(
                    id=match_group[0].id,
                    relevance=avg_score,
                    topics=topics,
                    article=article_content,
                )
            )

        return ArticleOverviewResponse(matches=match_items)

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
        profile = await SearchProfileRepository.get_search_profile_by_id(
            search_profile_id
        )
        has_organization_subscription_access = (
            await SubscriptionRepository.has_organization_subscription_access(
                profile.organization_id, article.subscription_id
            )
        )

        all_matches = await MatchRepository.get_matches_by_profile_and_article(
            search_profile_id=search_profile_id, article_id=article.id
        )

        topic_ids = {m.topic_id for m in all_matches if m.topic_id is not None}

        topic_names = await TopicsRepository.get_topic_names_by_ids(topic_ids)
        topic_keywords_map = await KeywordRepository.get_keywords_by_topic_ids(
            topic_ids
        )

        topic_items: dict[UUID, MatchTopicItem] = {}

        for m in all_matches:
            tid = m.topic_id
            if tid is None:
                continue

            score = round(m.score, 4)

            if tid not in topic_items or score > topic_items[tid].score:
                topic_items[tid] = MatchTopicItem(
                    id=tid,
                    name=topic_names.get(tid, ""),
                    score=score,
                    keywords=topic_keywords_map.get(tid, []),
                )

        topics = list(topic_items.values())

        entities_dict = (
            await ArticleEntityRepository.get_entities_multilang_by_article(
                article.id
            )
        )

        # Check if organization has subscription access and modify content accordingly
        if has_organization_subscription_access:
            article_text = {
                "de": article.content_de or "",
                "en": article.content_en or "",
            }
        else:
            article_text = {
                "de": None,
                "en": None,
            }
        publisher = None
        if article.subscription_id:
            async with async_session() as session:
                subscription = await SubscriptionRepository.get_by_id(
                    subscription_id=article.subscription_id, session=session
                )
                if subscription:
                    publisher = subscription.name
        return MatchDetailResponse(
            match_id=match.id,
            topics=topics,
            search_profile=MatchProfileInfo(id=profile.id, name=profile.name),
            article=MatchArticleOverviewContent(
                article_url=article.url or "",
                headline={
                    "de": article.title_de or "",
                    "en": article.title_en or "",
                },
                summary={
                    "de": article.summary_de or "",
                    "en": article.summary_en or "",
                },
                text=article_text,
                image_urls=[url for url in [article.image_url] if url],
                published=article.published_at,
                crawled=article.crawled_at,
                authors=article.authors or [],
                status=article.status,
                categories=article.categories or [],
                language=article.language,
                newspaper_id=article.subscription_id,
                publisher=publisher,
            ),
            entities=entities_dict,
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
        search_profile_name: str,
        search_profile_language: str,
        related_topics: List[KeywordSuggestionTopic],
        selected_topic: KeywordSuggestionTopic,
    ) -> KeywordSuggestionResponse:
        """
        Generate keyword suggestions based on the search profile information
        """
        try:
            article_vector_service = ArticleVectorService()

            def format_related_topics(
                topics: List[KeywordSuggestionTopic],
            ) -> str:
                if not topics:
                    return "--"
                return "\n".join(
                    f"{topic.topic_name}: {', '.join(topic.keywords)}"
                    for topic in topics
                )

            # Select the appropriate prompt based on the language
            if search_profile_language == Language.DE.value:
                prompt = KEYWORD_SUGGESTION_PROMPT_DE
            elif search_profile_language == Language.EN.value:
                prompt = KEYWORD_SUGGESTION_PROMPT_EN
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported language for keyword suggestions",
                )

            prompt = prompt.format(
                search_profile_name=search_profile_name,
                selected_topic_name=selected_topic.topic_name,
                selected_topic_keywords=", ".join(selected_topic.keywords),
                related_topics=format_related_topics(related_topics),
            )

            llm = LLMClient(TaskModelMapping.KEYWORD_SUGGESTION, max_retries=1)

            try:
                response = llm.generate_typed_response(
                    prompt, KeywordSuggestionResponse
                )
            except Exception as e:
                logger.error(
                    "LLM generation failed: %s", traceback.format_exc()
                )
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate keyword suggestions from LLM",
                )

            if not response:
                logger.error(
                    f"Empty response from LLM for profile '{search_profile_name}'"
                )
                raise HTTPException(
                    status_code=500,
                    detail="Received empty response from LLM",
                )

            suggestions_map = []

            for suggestion in response.suggestions:
                try:
                    docs = await article_vector_service.retrieve_by_similarity(
                        query=suggestion, score_threshold=0.5
                    )
                    suggestions_map.append((suggestion, len(docs)))
                except (UnexpectedResponse, QdrantException) as qe:
                    logger.error(
                        "Qdrant error while retrieving similarity for '%s': %s",
                        suggestion,
                        traceback.format_exc(),
                    )
                    raise HTTPException(
                        status_code=502,
                        detail="Failed to connect to vector search service",
                    )
                except Exception as e:
                    logger.error(
                        "Unexpected error during vector search: %s",
                        traceback.format_exc(),
                    )
                    raise HTTPException(
                        status_code=500,
                        detail="An error occurred during vector-based similarity search",
                    )

            suggestions_map.sort(key=lambda x: x[1], reverse=True)
            top_suggestions = [item[0] for item in suggestions_map[:5]]

            return KeywordSuggestionResponse(suggestions=top_suggestions)

        except HTTPException:
            raise  # re-raise to preserve existing HTTPExceptions
        except Exception as e:
            logger.error(
                "Unhandled exception in keyword suggestion: %s",
                traceback.format_exc(),
            )
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred during keyword suggestion generation",
            )

    @staticmethod
    async def delete_search_profile(
        profile_id: UUID, current_user: UserEntity
    ) -> None:
        search_profile = await SearchProfileRepository.get_by_id(profile_id)
        # Permit deletion if user is owner, superuser, or maintainer of the same org
        allow_delete = (
            current_user.id == search_profile.owner_id
            or current_user.is_superuser
            or (
                current_user.role == UserRole.maintainer
                and current_user.organization_id
                == search_profile.organization_id
            )
        )

        search_profile = (
            await SearchProfileRepository.get_search_profile_by_id(profile_id)
        )

        if not allow_delete:
            raise HTTPException(
                status_code=403, detail="Not allowed to delete this profile"
            )

        async with async_session() as session:
            try:
                # begin a transaction
                async with session.begin():
                    # delete dependent records
                    await MatchRepository.delete_for_search_profile(
                        session, profile_id
                    )
                    await ReportRepository.delete_for_search_profile(
                        session, profile_id
                    )
                    await SubscriptionRepository.delete_links_for_search_profile(
                        session, profile_id
                    )
                    await UserRepository.delete_links_for_search_profile(
                        session, profile_id
                    )

                    topic_ids = [topic.id for topic in search_profile.topics]
                    await TopicsRepository.delete_keyword_links_for_search_profile(
                        session, topic_ids
                    )
                    await TopicsRepository.delete_for_search_profile(
                        session, profile_id
                    )

                    # finally, delete the profile itself
                    await SearchProfileRepository.delete_by_id(
                        session, profile_id
                    )
            except Exception:
                # transaction is rolled back automatically on exception
                raise
