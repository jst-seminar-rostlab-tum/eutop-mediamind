import asyncio
from uuid import uuid4
from unittest.mock import AsyncMock, patch

from app.models import SearchProfile, User
from app.schemas.search_profile_schemas import SearchProfileUpdateRequest
from app.services.search_profiles_service import SearchProfiles


def test_get_available_search_profiles():
    with patch("app.services.search_profiles_service.SearchProfileRepository.get_accessible_profiles", new_callable=AsyncMock) as mock_get:
        current_user = {"id": "user1", "organization_id": "org1"}
        mock_get.return_value = [SearchProfile(id=uuid4())]

        result = asyncio.run(SearchProfiles.get_available_search_profiles(current_user))
        assert isinstance(result, list)
        assert all(isinstance(r, SearchProfile) for r in result)


def test_get_search_profile_with_access():
    with patch("app.services.search_profiles_service.SearchProfileRepository.get_by_id", new_callable=AsyncMock) as mock_get:
        search_profile_id = uuid4()
        current_user = {"id": "user1", "organization_id": "org1"}
        fake_profile = SearchProfile(
            id=search_profile_id,
            is_public=False,
            users=[User(id="user1")],
            organization_id="org2"
        )
        mock_get.return_value = fake_profile

        result = asyncio.run(SearchProfiles.get_search_profile(search_profile_id, current_user))
        assert result == fake_profile


def test_get_article_overview():
    with patch("app.services.search_profiles_service.MatchRepository.get_articles_by_profile", new_callable=AsyncMock) as mock_get:
        profile_id = uuid4()
        article = type("Article", (), {
            "id": uuid4(), "title": "Test", "url": "http://test", "author": "Author",
            "published_at": "2023-01-01", "language": "en", "category": "news", "summary": "summary"
        })()
        match = type("Match", (), {"article": article, "sorting_order": 1, "article_id": article.id})()
        mock_get.return_value = [match]

        result = asyncio.run(SearchProfiles.get_article_overview(profile_id))
        assert result.search_profile_id == profile_id
        assert len(result.articles) == 1
        assert result.articles[0].title == "Test"


def test_update_search_profile_success():
    with patch("app.services.search_profiles_service.SearchProfileRepository.get_by_id", new_callable=AsyncMock) as mock_get_by_id, \
         patch("app.services.search_profiles_service.SearchProfileRepository.update_by_id", new_callable=AsyncMock) as mock_update_by_id:

        profile_id = uuid4()
        owner_id = uuid4()
        current_user = {"id": str(owner_id)}

        data = SearchProfileUpdateRequest(
            id=profile_id,
            name="Updated name",
            public=True,
            owner=owner_id,
            is_editable=True
        )
        profile = SearchProfile(id=profile_id, created_by_id=str(owner_id))
        mock_get_by_id.return_value = profile
        mock_update_by_id.return_value = {"id": profile_id}

        result = asyncio.run(SearchProfiles.update_search_profile(profile_id, data, current_user))
        assert result == {"id": profile_id}


def test_get_match_detail_success():
    with patch("app.services.search_profiles_service.MatchRepository.get_match_by_id", new_callable=AsyncMock) as mock_get_match:
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

        result = asyncio.run(SearchProfiles.get_match_detail(profile_id, match_id))
        assert result.match_id == match_id
        assert result.title == "Test"
