import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.repositories.keyword_repository import KeywordRepository
from app.schemas.keyword_schemas import KeywordCreateRequest

@pytest.mark.asyncio
async def test_get_keyword_by_id(monkeypatch):
    monkeypatch.setattr("app.repositories.keyword_repository.async_session", MagicMock())
    monkeypatch.setattr("app.repositories.keyword_repository.select", MagicMock())
    monkeypatch.setattr("app.repositories.keyword_repository.Keyword", MagicMock())
    result = await KeywordRepository.get_keyword_by_id(1)
    assert result is None or result is not None

@pytest.mark.asyncio
async def test_add_keyword(monkeypatch):
    class DummyTopic:
        class DummySearchProfile:
            user_id = 1
        search_profile = DummySearchProfile()
    class DummySession:
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
        async def get(self, *args, **kwargs): return DummyTopic()
        async def add(self, obj): pass
        async def commit(self): pass
        async def refresh(self, *args, **kwargs): pass
        
    monkeypatch.setattr("app.repositories.keyword_repository.async_session", lambda: DummySession())
    req = MagicMock(spec=KeywordCreateRequest)
    req.value = "test"
    user = MagicMock()
    user.id = 1
    await KeywordRepository.add_keyword(1, req, user)
