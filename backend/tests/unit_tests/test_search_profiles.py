import asyncio
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.services.search_profiles_service import SearchProfileService


def test_get_article_overview():
    with patch(
        "app.services.search_profiles_service.MatchRepository.get_articles_by_profile",
        new_callable=AsyncMock,
    ) as mock_get:
        search_profile_id = uuid4()
        from datetime import datetime

        article = type(
            "Article",
            (),
            {
                "id": uuid4(),
                "title": "Test",
                "url": "http://test",
                "author": "Author",
                "published_at": datetime(2023, 1, 1),
                "language": "en",
                "category": "news",
                "summary": "summary",
            },
        )()

        match = type(
            "Match",
            (),
            {"article": article, "sorting_order": 1, "article_id": article.id},
        )()
        mock_get.return_value = [match]

        result = asyncio.run(
            SearchProfileService.get_article_overview(search_profile_id)
        )
        assert result.search_profile_id == search_profile_id
        assert len(result.articles) == 1
        assert result.articles[0].title == "Test"


def test_get_match_detail_success():
    with patch(
        "app.services.search_profiles_service.MatchRepository.get_match_by_id",
        new_callable=AsyncMock,
    ) as mock_get_match:
        search_profile_id = uuid4()
        match_id = uuid4()
        article = type(
            "Article",
            (),
            {
                "id": uuid4(),
                "title": "Test",
                "url": "http://test",
                "author": "Author",
                "published_at": "2023-01-01",
                "language": "en",
                "category": "news",
                "summary": "summary",
            },
        )()
        match = type(
            "Match",
            (),
            {
                "id": match_id,
                "comment": "good",
                "sorting_order": 1,
                "article": article,
            },
        )()
        mock_get_match.return_value = match

        result = asyncio.run(
            SearchProfileService.get_match_detail(search_profile_id, match_id)
        )
        assert result.match_id == match_id
        assert result.title == "Test"
