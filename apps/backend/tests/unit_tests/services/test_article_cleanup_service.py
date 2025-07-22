# 1%
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.article_cleanup_service import ArticleCleanupService


class DummyResult:
    def scalars(self):
        class DummyScalars:
            def all(self):
                return [1]

        return DummyScalars()

    def scalar(self):
        return 1

    def scalar_one_or_none(self):
        return None

    def all(self):
        return [1]


class DummySession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def execute(self, stmt):
        return DummyResult()


@pytest.mark.asyncio
async def test_cleanup_articles_older_than_days_normal(monkeypatch):
    service = ArticleCleanupService()
    # mock async_session and all internal methods
    monkeypatch.setattr(
        service,
        "_process_article_batch",
        AsyncMock(
            return_value={
                "articles_deleted": 1,
                "entities_deleted": 1,
                "keyword_links_deleted": 1,
                "matches_deleted": 1,
                "vector_store_deletions": 1,
                "errors": 0,
                "batch_size": 1,
            }
        ),
    )
    monkeypatch.setattr(
        "app.services.article_cleanup_service.async_session",
        lambda: DummySession(),
    )
    monkeypatch.setattr(
        "app.services.article_cleanup_service.logger", MagicMock()
    )
    stats = await service.cleanup_articles_older_than_days(
        days=1, batch_size=1
    )
    assert stats is not None


@pytest.mark.asyncio
async def test_delete_article_entities_empty():
    service = ArticleCleanupService()
    result = await service._delete_article_entities(MagicMock(), [])
    assert result == 0


@pytest.mark.asyncio
async def test_delete_article_keyword_links_empty():
    service = ArticleCleanupService()
    result = await service._delete_article_keyword_links(MagicMock(), [])
    assert result == 0


@pytest.mark.asyncio
async def test_delete_article_matches_empty():
    service = ArticleCleanupService()
    result = await service._delete_article_matches(MagicMock(), [])
    assert result == 0


@pytest.mark.asyncio
async def test_delete_from_vector_store_empty():
    service = ArticleCleanupService()
    result = await service._delete_from_vector_store([])
    assert result == 0


@pytest.mark.asyncio
async def test_delete_articles_empty():
    service = ArticleCleanupService()
    result = await service._delete_articles(MagicMock(), [])
    assert result == 0
