from collections import defaultdict
from typing import List
from uuid import UUID

from app.core.db import async_session
from app.repositories.article_repository import ArticleRepository
from app.repositories.keyword_repository import KeywordRepository
from app.repositories.match_repository import MatchRepository
from app.repositories.search_profile import SearchProfileRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.topics_repository import TopicsRepository
from app.schemas.articles_schemas import (
    ArticleOverviewResponse,
    MatchArticleOverviewContent,
    MatchDetailResponse,
    MatchItem,
    MatchTopicItem,
)
from app.schemas.match_schemas import MatchFeedbackRequest, MatchFilterRequest
from app.services.article_vector_service import ArticleVectorService


async def get_article_matches(
    search_profile_id: UUID,
    request: MatchFilterRequest,
) -> ArticleOverviewResponse:
    async with async_session():
        # load profile to get organization_id
        profile = await SearchProfileRepository.get_by_id(search_profile_id)
        if request.searchTerm:
            avs = ArticleVectorService()
            results = await avs.retrieve_by_similarity(
                query=request.searchTerm
            )
            relevance_map = {
                UUID(doc.metadata["id"]): score for doc, score in results
            }
            ids = set(relevance_map.keys())
            all_matches = await MatchRepository.get_matches_by_search_profile(
                search_profile_id
            )
            filtered = [
                m
                for m in all_matches
                if m.article
                and m.article.id in ids
                and request.startDate
                <= m.article.published_at.date()
                <= request.endDate
            ]
        else:
            all_matches = await MatchRepository.get_matches_by_search_profile(
                search_profile_id
            )
            filtered = [
                m
                for m in all_matches
                if m.article
                and request.startDate
                <= m.article.published_at.date()
                <= request.endDate
            ]

        if request.subscriptions:
            filtered = [
                m
                for m in filtered
                if await ArticleRepository.get_subscription_id_for_article(
                    m.article_id
                )
                in request.subscriptions
            ]
        if request.topics:
            topics_set = set(request.topics)
            filtered = [m for m in filtered if m.topic_id in topics_set]

        # sort
        if request.sorting == "RELEVANCE":
            filtered.sort(key=lambda x: getattr(x, "score", 0), reverse=True)
        else:
            filtered.sort(key=lambda x: x.article.published_at, reverse=True)

        # group by article
        grouped = defaultdict(list)
        for m in filtered:
            grouped[m.article_id].append(m)

        topic_ids = {m.topic_id for m in filtered if m.topic_id}
        names = await TopicsRepository.get_topic_names_by_ids(topic_ids)
        keywords_map = await KeywordRepository.get_keywords_by_topic_ids(
            topic_ids
        )

        items: List[MatchItem] = []
        for aid, group in grouped.items():
            total = 0
            topics = {}
            article = group[0].article
            has_access = await SubscriptionRepository.has_organization_subscription_access(  # noqa: E501
                profile.organization_id, article.subscription_id
            )
            for m in group:
                if m.topic_id and m.topic_id not in topics:
                    topics[m.topic_id] = MatchTopicItem(
                        id=m.topic_id,
                        name=names.get(m.topic_id, ""),
                        score=round(m.score, 4),
                        keywords=keywords_map.get(m.topic_id, []),
                    )
                    total += m.score
            topic_list = list(topics.values())
            avg = total / len(topic_list) if topic_list else 0
            content = MatchArticleOverviewContent(
                article_url=article.url or "",
                headline={
                    "de": article.title_de or "",
                    "en": article.title_en or "",
                },
                summary={
                    "de": article.summary_de or "",
                    "en": article.summary_en or "",
                },
                text=(
                    {
                        "de": article.content_de or "",
                        "en": article.content_en or "",
                    }
                    if has_access
                    else {"de": None, "en": None}
                ),
                image_urls=[article.image_url] if article.image_url else [],
                published=article.published_at,
                crawled=article.crawled_at,
                newspaper_id=article.subscription_id,
                authors=article.authors or [],
                categories=article.categories or [],
                status=article.status,
            )
            items.append(
                MatchItem(
                    id=group[0].id,
                    relevance=avg,
                    topics=topic_list,
                    article=content,
                )
            )

        return ArticleOverviewResponse(matches=items)


async def get_match_detail(
    search_profile_id: UUID,
    match_id: UUID,
) -> MatchDetailResponse | None:
    async with async_session():
        match = await MatchRepository.get_match_by_id(
            search_profile_id, match_id
        )
        if not match or not match.article:
            return None
        article = match.article
        profile = await SearchProfileRepository.get_search_profile_by_id(
            search_profile_id
        )
        has_access = (
            await SubscriptionRepository.has_organization_subscription_access(
                profile.organization_id, article.subscription_id
            )
        )
        all_matches = await MatchRepository.get_matches_by_profile_and_article(
            search_profile_id, article.id
        )

        topic_ids = {m.topic_id for m in all_matches if m.topic_id}
        names = await TopicsRepository.get_topic_names_by_ids(topic_ids)
        keywords_map = await KeywordRepository.get_keywords_by_topic_ids(
            topic_ids
        )

        best: dict[UUID, MatchTopicItem] = {}
        for m in all_matches:
            if m.topic_id:
                score = round(m.score, 4)
                if m.topic_id not in best or score > best[m.topic_id].score:
                    best[m.topic_id] = MatchTopicItem(
                        id=m.topic_id,
                        name=names.get(m.topic_id, ""),
                        score=score,
                        keywords=keywords_map.get(m.topic_id, []),
                    )
        topics = list(best.values())
        entities = await ArticleRepository.get_entities_by_article(article.id)

        return MatchDetailResponse(
            match_id=match.id,
            topics=topics,
            search_profile={"id": profile.id, "name": profile.name},
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
                text=(
                    {
                        "de": article.content_de or "",
                        "en": article.content_en or "",
                    }
                    if has_access
                    else {"de": None, "en": None}
                ),
                image_urls=[article.image_url] if article.image_url else [],
                published=article.published_at,
                crawled=article.crawled_at,
                authors=article.authors or [],
                categories=article.categories or [],
                newspaper_id=article.subscription_id,
                status=article.status,
            ),
            entities=entities,
        )


async def update_match_feedback(
    search_profile_id: UUID,
    match_id: UUID,
    data: MatchFeedbackRequest,
) -> bool:
    async with async_session():
        updated = await MatchRepository.update_match_feedback(
            search_profile_id=search_profile_id,
            match_id=match_id,
            comment=data.comment,
            reason=data.reason,
            ranking=data.ranking,
        )
    return updated is not None
