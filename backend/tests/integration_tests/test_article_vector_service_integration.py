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
    # Skip, falls kein Qdrant erreichbar ist
    try:
        client.get_collections()
    except Exception:
        pytest.skip("Qdrant server not available")
    yield client


@pytest.fixture
def temp_collection(qdrant_client):
    name = f"integration_test_{uuid.uuid4().hex}"
    # sicherstellen, dass sie nicht existiert
    if qdrant_client.collection_exists(name):
        qdrant_client.delete_collection(collection_name=name)
    yield name
    # aufräumen
    qdrant_client.delete_collection(collection_name=name)


@pytest.fixture
def service(monkeypatch, temp_collection):
    # Override in den Configs
    from app.core.config import configs

    configs.ARTICLE_VECTORS_COLLECTION = temp_collection
    # Klasse initiiert und legt die neue Collection an
    svc = ArticleVectorService()
    return svc


def test_add_articles_and_count(qdrant_client, service):
    # zu Beginn leer
    cnt = qdrant_client.count(collection_name=service.collection_name).count
    assert cnt == 0

    # 3 Artikel hinzufügen
    articles = [make_article() for _ in range(3)]
    service.add_articles(articles)

    # nun sollten 3 Punkte in Qdrant liegen
    cnt = qdrant_client.count(collection_name=service.collection_name).count
    assert cnt == 3


@pytest.mark.asyncio
async def test_add_article_and_count(qdrant_client, service, monkeypatch):
    art = make_article()

    # Repository so patchen, dass get_article_by_id unseren Dummy zurückgibt
    async def fake_get(article_id):
        return art

    monkeypatch.setattr(ArticleRepository, "get_article_by_id", fake_get)

    # leer starten
    assert (
        qdrant_client.count(collection_name=service.collection_name).count == 0
    )

    # einzelne Methode
    await service.add_article(art.id)

    # genau 1 neuer Punkt
    assert (
        qdrant_client.count(collection_name=service.collection_name).count == 1
    )


@pytest.mark.asyncio
async def test_index_summarized_articles_and_count(
    qdrant_client, service, monkeypatch
):
    # Zwei Seiten mit je 2 Artikeln, dann leer
    page1 = [make_article(summary=f"page1-{i}") for i in range(2)]
    page2 = [make_article(summary=f"page2-{i}") for i in range(2)]

    async def fake_list(limit: int, offset: int):
        if offset == 0:
            return page1
        if offset == 2:
            return page2
        return []

    monkeypatch.setattr(
        ArticleRepository, "list_articles_with_summary", fake_list
    )

    # vorher 0
    assert (
        qdrant_client.count(collection_name=service.collection_name).count == 0
    )

    # indexieren
    await service.index_summarized_articles_to_vector_store(page_size=2)

    # jetzt 4
    assert (
        qdrant_client.count(collection_name=service.collection_name).count == 4
    )
