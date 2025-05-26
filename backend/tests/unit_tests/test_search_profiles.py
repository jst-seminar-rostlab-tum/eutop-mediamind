import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch

from app.models import SearchProfile
from app.services.search_profiles_service import SearchProfiles

@pytest.mark.asyncio
@patch("app.services.search_profiles_service.SearchProfileRepository.get_accessible_profiles", new_callable=AsyncMock)
async def test_get_available_search_profiles(mock_get_accessible_profiles):
    current_user = {"id": "user1", "organization_id": "org1"}
    mock_get_accessible_profiles.return_value = [SearchProfile(id=uuid4())]

    result = await SearchProfiles.get_available_search_profiles(current_user)

    assert isinstance(result, list)
    assert all(isinstance(r, SearchProfile) for r in result)



@pytest.mark.asyncio
@patch("app.services.search_profiles_service.MatchRepository.get_articles_by_profile", new_callable=AsyncMock)
async def test_get_article_overview(mock_get_articles):
    profile_id = uuid4()
    article = type("Article", (), {
        "id": uuid4(), "title": "Test", "url": "http://test", "author": "Author",
        "published_at": "2023-01-01", "language": "en", "category": "news", "summary": "summary"
    })()
    match = type("Match", (), {"article": article, "sorting_order": 1, "article_id": article.id})()
    mock_get_articles.return_value = [match]

    result = await SearchProfiles.get_article_overview(profile_id)

    assert result.search_profile_id == profile_id
    assert len(result.articles) == 1
    assert result.articles[0].title == "Test"


@pytest.mark.asyncio
@patch("app.services.search_profiles_service.MatchRepository.get_match_by_id", new_callable=AsyncMock)
async def test_get_match_detail_success(mock_get_match):
    profile_id = uuid4()
    match_id = uuid4()
    article = type("Article", (), {
        "id": uuid4(), "title": "Test", "url": "http://test", "author": "Author",
        "published_at": "2023-01-01", "language": "en", "category": "news", "summary": "summary"
    })()
    match = type("Match", (), {
        "id": match_id, "comment": "good", "sorting_order": 1, "article": article
    })()
    mock_get_match.return_value = match

    result = await SearchProfiles.get_match_detail(profile_id, match_id)

    assert result.match_id == match_id
    assert result.title == "Test"
