import asyncio
import uuid

import pytest

from app.core.db import get_qdrant_connection
from app.models import Article
from app.repositories.article_repository import ArticleRepository
from app.services.article_vector_service import ArticleVectorService


def make_article(
    id: uuid.UUID = None,
    summary: str = "Integration summary",
    title: str = "Integration Title",
    subscription_id: uuid.UUID = None,
) -> Article:
    return Article(
        id=id or uuid.uuid4(),
        summary=summary,
        title=title,
        subscription_id=subscription_id or uuid.uuid4(),
        content="",
        created_at=None,
        updated_at=None,
    )


@pytest.fixture(scope="module")
def qdrant_client():
    client = get_qdrant_connection()
    try:
        client.get_collections()
    except Exception:
        pytest.skip("Qdrant server not available")
    yield client


@pytest.fixture
def temp_collection(qdrant_client):
    name = f"integration_test_{uuid.uuid4().hex}"
    if qdrant_client.collection_exists(name):
        qdrant_client.delete_collection(collection_name=name)
    yield name
    qdrant_client.delete_collection(collection_name=name)


@pytest.fixture
def service(monkeypatch, temp_collection):
    from app.core.config import configs

    configs.ARTICLE_VECTORS_COLLECTION = temp_collection
    svc = ArticleVectorService()
    return svc


def test_add_articles_and_count(qdrant_client, service):

    cnt = qdrant_client.count(collection_name=service.collection_name).count
    assert cnt == 0

    # add 3 articles
    articles = [make_article() for _ in range(3)]
    asyncio.run(service.add_articles(articles))

    # now there should be 3 points in Qdrant
    cnt = qdrant_client.count(collection_name=service.collection_name).count
    assert cnt == 3


@pytest.mark.asyncio
async def test_add_article_and_count(qdrant_client, service, monkeypatch):
    art = make_article()

    # patch the repository so that get_article_by_id returns our dummy
    async def fake_get(article_id):
        return art

    monkeypatch.setattr(ArticleRepository, "get_article_by_id", fake_get)

    # start empty
    assert (
        qdrant_client.count(collection_name=service.collection_name).count == 0
    )

    # single method
    await service.add_article(art.id)

    # exactly one new point
    assert (
        qdrant_client.count(collection_name=service.collection_name).count == 1
    )


@pytest.mark.asyncio
async def test_index_summarized_articles_and_count(
    qdrant_client, service, monkeypatch
):
    # two pages with 2 articles each, then empty
    page1 = [make_article(summary=f"page1-{i}") for i in range(2)]
    page2 = [make_article(summary=f"page2-{i}") for i in range(2)]

    async def fake_list(limit: int, date_start=None, date_end=None):
        if not hasattr(fake_list, "call_count"):
            fake_list.call_count = 0
        fake_list.call_count += 1

        if fake_list.call_count == 1:
            return page1 + page2
        return []

    async def fake_update(article):
        # Mock update to avoid database access
        pass

    monkeypatch.setattr(
        ArticleRepository, "list_articles_with_summary", fake_list
    )
    monkeypatch.setattr(ArticleRepository, "update_article", fake_update)

    # previously 0
    assert (
        qdrant_client.count(collection_name=service.collection_name).count == 0
    )

    # index
    await service.index_summarized_articles_to_vector_store(page_size=2)

    # now 4
    assert (
        qdrant_client.count(collection_name=service.collection_name).count == 4
    )
