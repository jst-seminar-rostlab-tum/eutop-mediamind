# flake8: noqa: E501
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.schemas.articles_schemas import (
    MatchDetailResponse,
)
from app.schemas.match_schemas import MatchFilterRequest
from app.services.search_profiles_service import SearchProfileService


@patch(
    "app.services.search_profiles_service.SubscriptionRepository.has_organization_subscription_access",
    new_callable=AsyncMock,
)
@patch(
    "app.services.search_profiles_service.SearchProfileRepository.get_by_id",
    new_callable=AsyncMock,
)
@patch(
    "app.services.search_profiles_service.ArticleRepository.get_subscription_id_for_article",
    new_callable=AsyncMock,
)
@patch(
    "app.services.search_profiles_service.TopicsRepository.get_topic_names_by_ids",
    new_callable=AsyncMock,
)
@patch(
    "app.services.search_profiles_service.KeywordRepository.get_keywords_by_topic_ids",
    new_callable=AsyncMock,
)
@patch(
    "app.services.search_profiles_service.MatchRepository.get_matches_by_search_profile",
    new_callable=AsyncMock,
)
def test_get_article_overview(
    mock_get_matches,
    mock_get_keywords,
    mock_get_topic_names,
    mock_get_subscription_id,
    mock_get_profile,
    mock_has_subscription_access,
):
    search_profile_id = uuid4()

    # mock search profile
    fake_search_profile = type(
        "SearchProfile",
        (),
        {
            "id": search_profile_id,
            "name": "Test Profile",
            "organization_id": uuid4(),
        },
    )()

    # mock article & match
    article = type(
        "Article",
        (),
        {
            "id": uuid4(),
            "title_de": "Test",
            "title_en": "Test",
            "summary_de": "summary",
            "summary_en": "",
            "content_de": "some text",
            "content_en": "",
            "url": "http://test",
            "authors": ["Author"],
            "categories": ["News"],
            "published_at": datetime(2023, 1, 1),
            "crawled_at": datetime(2023, 1, 2),
            "language": "en",
            "subscription_id": uuid4(),
            "status": "scraped",
            "image_url": "http://test",
        },
    )()

    match = type(
        "Match",
        (),
        {
            "id": uuid4(),
            "article": article,
            "sorting_order": 1,
            "article_id": article.id,
            "topic_id": uuid4(),
            "score": 0.8,
        },
    )()

    mock_get_matches.return_value = [match]
    mock_get_subscription_id.return_value = article.subscription_id
    mock_get_topic_names.return_value = {match.topic_id: "TestTopic"}
    mock_get_keywords.return_value = {match.topic_id: ["keyword1", "keyword2"]}
    mock_get_profile.return_value = fake_search_profile
    mock_has_subscription_access.return_value = True

    request = MatchFilterRequest(
        searchTerm=None,
        startDate=datetime(2022, 12, 31).date(),
        endDate=datetime(2023, 1, 2).date(),
        subscriptions=[],
        topics=[],
        sorting="DATE",
    )

    result = asyncio.run(
        SearchProfileService.get_article_matches(
            search_profile_id=search_profile_id,
            request=request,
        )
    )

    assert len(result.matches) == 1
    assert result.matches[0].article.headline["en"] == "Test"


def test_get_match_detail_success():
    search_profile_id = uuid4()
    match_id = uuid4()
    topic_id = uuid4()

    fake_article = type(
        "Article",
        (),
        {
            "id": uuid4(),
            "title_de": "Titel",
            "title_en": "Title",
            "summary_de": "Zusammenfassung",
            "summary_en": "Summary",
            "content_de": "Inhalt",
            "content_en": "Content",
            "url": "http://test",
            "image_url": "http://image.com/image.jpg",
            "authors": ["Alice"],
            "categories": ["News"],
            "published_at": datetime(2023, 1, 1),
            "crawled_at": datetime(2023, 1, 2),
            "language": "en",
            "subscription_id": uuid4(),
            "status": "scraped",
        },
    )()

    fake_match = type(
        "Match",
        (),
        {
            "id": match_id,
            "article": fake_article,
            "article_id": fake_article.id,
            "topic_id": topic_id,
            "score": 0.75,
        },
    )()

    fake_profile = type(
        "SearchProfile",
        (),
        {
            "id": search_profile_id,
            "name": "My Profile",
            "organization_id": uuid4(),
        },
    )()

    with (
        patch(
            "app.repositories.match_repository.MatchRepository.get_match_by_id",
            new_callable=AsyncMock,
        ) as mock_get_match,
        patch(
            "app.repositories.match_repository.MatchRepository.get_matches_by_profile_and_article",
            new_callable=AsyncMock,
        ) as mock_get_matches,
        patch(
            "app.repositories.search_profile_repository.SearchProfileRepository.get_search_profile_by_id",
            new_callable=AsyncMock,
        ) as mock_get_profile,
        patch(
            "app.repositories.topics_repository.TopicsRepository.get_topic_names_by_ids",
            new_callable=AsyncMock,
        ) as mock_get_topic_names,
        patch(
            "app.repositories.keyword_repository.KeywordRepository.get_keywords_by_topic_ids",
            new_callable=AsyncMock,
        ) as mock_get_keywords,
        patch(
            "app.repositories.entity_repository.ArticleEntityRepository.get_entities_multilang_by_article",
            new_callable=AsyncMock,
        ) as mock_get_entities,
        patch(
            "app.repositories.subscription_repository.SubscriptionRepository.has_organization_subscription_access",
            new_callable=AsyncMock,
        ) as mock_has_subscription_access,
        patch(
            "app.repositories.subscription_repository.SubscriptionRepository.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_subscription_by_id,
    ):
        mock_get_match.return_value = fake_match
        mock_get_matches.return_value = [fake_match]
        mock_get_profile.return_value = fake_profile
        mock_get_topic_names.return_value = {topic_id: "Environment"}
        mock_get_keywords.return_value = {topic_id: ["green"]}
        mock_get_entities.return_value = {
            "industry": [{"de": "Automobil", "en": "Automotive"}],
            "event": [{"de": "Fusion", "en": "Merger"}],
            "organization": ["BMW"],
        }
        mock_has_subscription_access.return_value = True
        fake_subscription = type(
            "Subscription", (), {"name": "Test Publisher"}
        )()
        mock_get_subscription_by_id.return_value = fake_subscription

        result: MatchDetailResponse = asyncio.run(
            SearchProfileService.get_match_detail(search_profile_id, match_id)
        )

    assert result.match_id == match_id
    assert result.topics[0].id == topic_id
    assert result.topics[0].score == round(fake_match.score, 4)
    assert result.topics[0].keywords == ["green"]
    assert result.article.headline["en"] == "Title"
    assert result.article.article_url == fake_article.url
    assert result.search_profile.name == "My Profile"
    assert result.entities == {
        "industry": [{"de": "Automobil", "en": "Automotive"}],
        "event": [{"de": "Fusion", "en": "Merger"}],
        "organization": ["BMW"],
    }
