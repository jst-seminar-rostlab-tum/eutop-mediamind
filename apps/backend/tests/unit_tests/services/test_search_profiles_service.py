import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

import app.services.search_profiles_service as sps
from app.schemas.articles_schemas import (
    ArticleOverviewResponse,
    MatchDetailResponse,
)
from app.schemas.match_schemas import MatchFeedbackRequest, MatchFilterRequest
from app.schemas.search_profile_schemas import (
    SearchProfileDetailResponse,
    SearchProfileUpdateRequest,
)
from app.schemas.subscription_schemas import (
    SetSearchProfileSubscriptionsRequest,
    SubscriptionSummary,
)
from app.schemas.topic_schemas import TopicResponse


@pytest.mark.asyncio
async def test_get_extended_by_id_none():
    user = Dummy()
    user.id = uuid4()
    user.role = sps.UserRole.maintainer
    user.is_superuser = False
    user.organization_id = uuid4()
    with patch.object(
        sps.SearchProfileRepository,
        "get_accessible_profile_by_id",
        new=AsyncMock(return_value=None),
    ):
        result = await sps.SearchProfileService.get_extended_by_id(
            uuid4(), user
        )
        assert result is None


@pytest.mark.asyncio
async def test_update_search_profile_not_found():
    user = Dummy()
    user.id = uuid4()
    user.organization_id = uuid4()
    user.role = sps.UserRole.maintainer
    user.is_superuser = False
    with patch.object(
        sps.SearchProfileRepository,
        "get_accessible_profile_by_id",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(HTTPException) as exc:
            await sps.SearchProfileService.update_search_profile(
                uuid4(),
                SearchProfileUpdateRequest(
                    name="test",
                    is_public=True,
                    owner_id=user.id,
                    language="en",
                    topics=[],
                    subscriptions=[],
                    can_read_user_ids=[],
                    can_edit_user_ids=[],
                    organization_emails=[],
                    profile_emails=[],
                ),
                user,
            )
        assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_search_profile_forbidden():
    user = Dummy()
    user.id = uuid4()
    user.organization_id = uuid4()
    user.role = sps.UserRole.member
    user.is_superuser = False
    db_profile = Dummy()
    db_profile.created_by_id = uuid4()
    db_profile.organization_id = uuid4()
    db_profile.is_public = False
    with patch.object(
        sps.SearchProfileRepository,
        "get_accessible_profile_by_id",
        new=AsyncMock(return_value=db_profile),
    ):
        with pytest.raises(HTTPException) as exc:
            await sps.SearchProfileService.update_search_profile(
                uuid4(),
                SearchProfileUpdateRequest(
                    name="test",
                    is_public=True,
                    owner_id=user.id,
                    language="en",
                    topics=[],
                    subscriptions=[],
                    can_read_user_ids=[],
                    can_edit_user_ids=[],
                    organization_emails=[],
                    profile_emails=[],
                ),
                user,
            )
        assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_get_match_detail_none():
    with patch.object(
        sps.MatchRepository,
        "get_match_by_id",
        new=AsyncMock(return_value=None),
    ):
        resp = await sps.SearchProfileService.get_match_detail(
            uuid4(), uuid4()
        )
        assert resp is None


@pytest.mark.asyncio
async def test_get_match_detail_article_none():
    match = Dummy()
    match.id = uuid4()
    match.article = None
    with patch.object(
        sps.MatchRepository,
        "get_match_by_id",
        new=AsyncMock(return_value=match),
    ):
        resp = await sps.SearchProfileService.get_match_detail(
            uuid4(), uuid4()
        )
        assert resp is None


@pytest.mark.asyncio
async def test_delete_search_profile_forbidden():
    user = Dummy()
    user.id = uuid4()
    user.organization_id = uuid4()
    user.role = sps.UserRole.member
    user.is_superuser = False
    search_profile = Dummy()
    search_profile.owner_id = uuid4()
    search_profile.organization_id = uuid4()
    search_profile.topics = []
    with patch.object(
        sps.SearchProfileRepository,
        "get_by_id",
        new=AsyncMock(return_value=search_profile),
    ):
        with patch.object(
            sps.SearchProfileRepository,
            "get_search_profile_by_id",
            new=AsyncMock(return_value=search_profile),
        ):
            with pytest.raises(HTTPException) as exc:
                await sps.SearchProfileService.delete_search_profile(
                    uuid4(), user
                )
            assert exc.value.status_code == 403


class Dummy:
    pass


@pytest.mark.asyncio
async def test_get_available_search_profiles():
    user = Dummy()
    user.id = uuid4()
    user.organization_id = uuid4()
    user.role = "user"
    user.is_superuser = False
    profile = Dummy()
    with patch.object(
        sps.SearchProfileRepository,
        "get_accessible_profiles",
        new=AsyncMock(return_value=[profile]),
    ):
        with patch.object(
            sps.SearchProfileService,
            "_build_profile_response",
            new=AsyncMock(return_value="resp"),
        ):
            result = (
                await sps.SearchProfileService.get_available_search_profiles(
                    user
                )
            )
            assert result == ["resp"]


@pytest.mark.asyncio
async def test__build_profile_response_variants():
    user = Dummy()
    user.id = uuid4()
    user.organization_id = uuid4()
    user.is_superuser = True
    profile = Dummy()
    profile.created_by_id = user.id
    profile.owner_id = user.id
    profile.can_edit_user_ids = [user.id]
    profile.can_read_user_ids = [user.id]
    profile.organization_emails = ["a@test.com"]
    profile.profile_emails = ["b@test.com"]
    profile.topics = [TopicResponse(id=uuid4(), name="topic", keywords=[])]
    profile.id = uuid4()
    profile.name = "n"
    profile.is_public = True
    profile.subscriptions = [
        SubscriptionSummary(
            id=uuid4(), name="test", is_active=True, is_subscribed=True
        )
    ]
    profile.new_articles_count = 0
    with patch.object(
        sps.SubscriptionRepository,
        "get_all_subscriptions_with_search_profile",
        new=AsyncMock(
            return_value=[
                SubscriptionSummary(
                    id=uuid4(), name="test", is_active=True, is_subscribed=True
                )
            ]
        ),
    ):
        with patch.object(
            sps.MatchRepository,
            "get_recent_match_count_by_profile_id",
            new=AsyncMock(return_value=3),
        ):
            resp = await sps.SearchProfileService._build_profile_response(
                profile, user
            )
            assert isinstance(resp, SearchProfileDetailResponse)
            assert resp.is_owner
            assert resp.is_editor
            assert resp.is_reader
            assert resp.organization_emails == ["a@test.com"]
            assert resp.profile_emails == ["b@test.com"]
            assert isinstance(resp.subscriptions[0], SubscriptionSummary)
            assert resp.new_articles_count == 3


def test__build_topic_response():
    topic = Dummy()
    topic.id = uuid4()
    topic.name = "t"
    topic.keywords = [Dummy() for _ in range(2)]
    topic.keywords[0].name = "k1"
    topic.keywords[1].name = "k2"
    resp = sps.SearchProfileService._build_topic_response(topic)
    assert isinstance(resp, TopicResponse)
    assert resp.keywords == ["k1", "k2"]


@pytest.mark.asyncio
async def test_update_search_profile_permission():
    user = Dummy()
    user.id = uuid4()
    user.organization_id = uuid4()
    user.role = sps.UserRole.maintainer
    user.is_superuser = False
    db_profile = Dummy()
    db_profile.created_by_id = uuid4()
    db_profile.organization_id = user.organization_id
    db_profile.is_public = True
    update_data = SearchProfileUpdateRequest(
        name="test",
        is_public=True,
        owner_id=user.id,
        language="en",
        topics=[],
        subscriptions=[],
        can_read_user_ids=[],
        can_edit_user_ids=[],
        organization_emails=[],
        profile_emails=[],
    )
    with patch.object(
        sps.SearchProfileRepository,
        "get_accessible_profile_by_id",
        new=AsyncMock(return_value=db_profile),
    ):
        with patch.object(
            sps.SearchProfileRepository, "update_profile", new=AsyncMock()
        ):
            with patch.object(
                sps.SearchProfileService,
                "_build_profile_response",
                new=AsyncMock(return_value="resp"),
            ):
                resp = await sps.SearchProfileService.update_search_profile(
                    uuid4(), update_data, user
                )
                assert resp == "resp"


@pytest.mark.asyncio
async def test_get_article_matches():
    search_profile_id = uuid4()
    user = Dummy()
    request = MatchFilterRequest(
        startDate=datetime.now().date(),
        endDate=datetime.now().date(),
        sorting="RELEVANCE",
    )
    match = Dummy()
    match.id = uuid4()
    match.article_id = uuid4()
    match.article = Dummy()
    match.article.published_at = datetime.now(timezone.utc)
    match.article.categories = []
    match.article.content_de = "de"
    match.article.content_en = "en"
    match.article.url = "url"
    match.article.title_de = "td"
    match.article.title_en = "te"
    match.article.summary_de = "sd"
    match.article.summary_en = "se"
    match.article.image_url = None
    match.article.crawled_at = datetime.now(timezone.utc)
    match.article.subscription_id = uuid4()
    match.article.authors = []
    match.article.status = "scraped"
    match.article.language = "en"
    match.topic_id = uuid4()
    match.score = 1.0
    dummy_profile = Dummy()
    dummy_profile.organization_id = uuid4()
    with patch.object(
        sps.SearchProfileRepository,
        "get_by_id",
        new=AsyncMock(return_value=dummy_profile),
    ):
        with patch.object(
            sps.MatchRepository,
            "get_matches_by_search_profile",
            new=AsyncMock(return_value=[match]),
        ):
            with patch.object(
                sps.TopicsRepository,
                "get_topic_names_by_ids",
                new=AsyncMock(return_value={match.topic_id: "topic"}),
            ):
                with patch.object(
                    sps.KeywordRepository,
                    "get_keywords_by_topic_ids",
                    new=AsyncMock(return_value={match.topic_id: ["kw"]}),
                ):
                    with patch.object(
                        sps.SubscriptionRepository,
                        "has_organization_subscription_access",
                        new=AsyncMock(return_value=True),
                    ):
                        resp = (
                            await sps.SearchProfileService.get_article_matches(
                                search_profile_id, request
                            )
                        )
                        assert isinstance(resp, ArticleOverviewResponse)
                        assert resp.matches


@pytest.mark.asyncio
async def test_get_match_detail():
    search_profile_id = uuid4()
    match_id = uuid4()
    match = Dummy()
    match.id = match_id
    match.article = Dummy()
    match.article.id = uuid4()
    match.article.content_de = "de"
    match.article.content_en = "en"
    match.article.url = "url"
    match.article.title_de = "td"
    match.article.title_en = "te"
    match.article.summary_de = "sd"
    match.article.summary_en = "se"
    match.article.image_url = None
    match.article.published_at = datetime.now(timezone.utc)
    match.article.crawled_at = datetime.now(timezone.utc)
    match.article.authors = []
    match.article.status = "scraped"
    match.article.categories = []
    match.article.language = "en"
    match.article.subscription_id = uuid4()
    match.topic_id = uuid4()
    match.score = 1.0
    profile = Dummy()
    profile.id = uuid4()
    profile.name = "n"
    profile.organization_id = uuid4()
    with patch.object(
        sps.MatchRepository,
        "get_match_by_id",
        new=AsyncMock(return_value=match),
    ):
        with patch.object(
            sps.SearchProfileRepository,
            "get_search_profile_by_id",
            new=AsyncMock(return_value=profile),
        ):
            with patch.object(
                sps.SubscriptionRepository,
                "has_organization_subscription_access",
                new=AsyncMock(return_value=True),
            ):
                with patch.object(
                    sps.MatchRepository,
                    "get_matches_by_profile_and_article",
                    new=AsyncMock(return_value=[match]),
                ):
                    with patch.object(
                        sps.TopicsRepository,
                        "get_topic_names_by_ids",
                        new=AsyncMock(return_value={match.topic_id: "topic"}),
                    ):
                        with patch.object(
                            sps.KeywordRepository,
                            "get_keywords_by_topic_ids",
                            new=AsyncMock(
                                return_value={match.topic_id: ["kw"]}
                            ),
                        ):
                            with patch.object(
                                sps.ArticleEntityRepository,
                                "get_entities_multilang_by_article",
                                new=AsyncMock(return_value={}),
                            ):
                                resp = await sps.SearchProfileService.get_match_detail(
                                    search_profile_id, match_id
                                )
                                assert isinstance(resp, MatchDetailResponse)


@pytest.mark.asyncio
async def test_update_match_feedback():
    with patch.object(
        sps.MatchRepository,
        "update_match_feedback",
        new=AsyncMock(return_value=True),
    ):
        req = MatchFeedbackRequest(comment="c", reason="bad source", ranking=1)
        result = await sps.SearchProfileService.update_match_feedback(
            uuid4(), uuid4(), req
        )
        assert result is True


@pytest.mark.asyncio
async def test_get_all_subscriptions_for_profile():
    with patch.object(
        sps.SubscriptionRepository,
        "get_all_subscriptions_with_search_profile",
        new=AsyncMock(return_value=["s"]),
    ):
        result = (
            await sps.SearchProfileService.get_all_subscriptions_for_profile(
                uuid4()
            )
        )
        assert result == ["s"]


@pytest.mark.asyncio
async def test_set_search_profile_subscriptions():
    req = SetSearchProfileSubscriptionsRequest(
        search_profile_id=uuid4(),
        subscriptions=[
            SubscriptionSummary(
                id=uuid4(), name="test", is_active=True, is_subscribed=True
            )
        ],
    )
    with patch.object(
        sps.SubscriptionRepository,
        "set_subscriptions_for_profile",
        new=AsyncMock(),
    ):
        await sps.SearchProfileService.set_search_profile_subscriptions(req)
