import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.repositories.topics_repository import TopicsRepository
from app.schemas.topic_schemas import TopicCreateOrUpdateRequest

class DummyResult:
    def scalars(self):
        class DummyScalars:
            def all(self): return []
        return DummyScalars()
    def scalar_one_or_none(self): return None
    def all(self): return []

class DummySession:
    async def __aenter__(self): return self
    async def __aexit__(self, exc_type, exc, tb): pass
    async def execute(self, *args, **kwargs): return DummyResult()
    async def get(self, *args, **kwargs):
        class DummyTopic:
            name = "topic"
        return DummyTopic()

@pytest.mark.asyncio
async def test_get_topics_by_search_profile(monkeypatch):
    monkeypatch.setattr("app.repositories.topics_repository.async_session", lambda: DummySession())
    user = MagicMock()
    await TopicsRepository.get_topics_by_search_profile(1, user)

@pytest.mark.asyncio
async def test_add_topic(monkeypatch):
    class DummySession:
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
        async def add(self, obj): pass
        async def commit(self): pass
        async def refresh(self, obj): pass
        
    monkeypatch.setattr("app.repositories.topics_repository.async_session", lambda: DummySession())
    user = MagicMock()
    req = MagicMock(spec=TopicCreateOrUpdateRequest)
    req.name = "topic"
    await TopicsRepository.add_topic(1, req, user)
