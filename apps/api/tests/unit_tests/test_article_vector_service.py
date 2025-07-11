import uuid
from unittest.mock import MagicMock

import pytest
from langchain_core.documents import Document

from app.models import Article
from app.services.article_vector_service import ArticleVectorService


def make_article(
    id=None, summary="Test summary", title="Test Title", subscription_id=None
):
    return Article(
        id=id or uuid.uuid4(),
        summary=summary,
        title=title,
        subscription_id=subscription_id or uuid.uuid4(),
        content="Original content",
        created_at=None,
        updated_at=None,
    )


@pytest.fixture(autouse=True)
def patch_qdrant_and_store(monkeypatch):
    # Dummy Qdrant client
    dummy_client = MagicMock()
    dummy_client.collection_exists.return_value = False
    monkeypatch.setattr(
        "app.services.article_vector_service.get_qdrant_connection",
        lambda: dummy_client,
    )
    # Dummy vector store
    dummy_store = MagicMock()
    monkeypatch.setattr(
        "app.services.article_vector_service.QdrantVectorStore",
        lambda *args, **kwargs: dummy_store,
    )
    return dummy_client, dummy_store


def test_create_collection_safe_when_missing(patch_qdrant_and_store):
    client, _ = patch_qdrant_and_store
    service = ArticleVectorService()
    client.collection_exists.assert_called_with(service.collection_name)
    client.create_collection.assert_called_once()


def test_create_collection_safe_when_exists(patch_qdrant_and_store):
    client, _ = patch_qdrant_and_store
    client.collection_exists.return_value = True
    service = ArticleVectorService()  # noqa: F841
    client.create_collection.assert_not_called()


def test_delete_collection(monkeypatch, patch_qdrant_and_store):
    client, _ = patch_qdrant_and_store
    client.collection_exists.return_value = True
    service = ArticleVectorService()
    service.delete_collection("foo")
    client.collection_exists.assert_called_with("foo")
    client.delete_collection.assert_called_with(collection_name="foo")


def test_delete_collection_noop_when_missing(patch_qdrant_and_store):
    client, _ = patch_qdrant_and_store
    client.collection_exists.return_value = False
    service = ArticleVectorService()
    service.delete_collection("bar")
    client.delete_collection.assert_not_called()


def test_get_list_of_collections(patch_qdrant_and_store):
    client, _ = patch_qdrant_and_store
    client.get_collections.return_value = ["col1", "col2"]
    service = ArticleVectorService()
    assert service.get_list_of_collections() == ["col1", "col2"]


@pytest.mark.asyncio
async def test_add_articles_calls_vector_store(
    monkeypatch, patch_qdrant_and_store
):
    _, store = patch_qdrant_and_store

    # Mock the ArticleRepository.update_article to avoid database calls
    async def mock_update_article(article):
        return None

    monkeypatch.setattr(
        "app.repositories.article_repository.ArticleRepository.update_article",
        mock_update_article,
    )

    articles = [
        make_article(
            id=uuid.UUID(int=i), subscription_id=uuid.UUID(int=i + 10)
        )
        for i in range(1, 4)
    ]
    service = ArticleVectorService()
    await service.add_articles(articles)
    store.add_documents.assert_called_once()
    docs = store.add_documents.call_args.kwargs["documents"]
    ids = store.add_documents.call_args.kwargs["ids"]
    for art, doc, id_ in zip(articles, docs, ids):
        assert isinstance(doc, Document)
        assert doc.page_content == art.summary
        assert str(doc.metadata["id"]) == str(art.id)
        assert str(id_) == str(art.id)


@pytest.mark.asyncio
async def test_retrieve_by_similarity_delegates_to_store(
    patch_qdrant_and_store,
):
    _, store = patch_qdrant_and_store
    store.similarity_search_with_score.return_value = [
        (Document(page_content="x", metadata={}), 0.9)
    ]
    service = ArticleVectorService()
    results = await service.retrieve_by_similarity(
        "query", score_threshold=0.5
    )
    assert results == [(Document(page_content="x", metadata={}), 0.9)]


@pytest.mark.asyncio
async def test_add_article_with_valid_summary(
    monkeypatch, patch_qdrant_and_store
):
    _, store = patch_qdrant_and_store
    art = make_article()

    async def fake_get(aid):
        return art

    monkeypatch.setattr(
        "app.repositories.article_repository."
        "ArticleRepository.get_article_by_id",
        fake_get,
    )
    service = ArticleVectorService()
    await service.add_article(art.id)
    store.add_documents.assert_called_once()


@pytest.mark.asyncio
async def test_add_article_missing_or_empty_summary_logs_error(
    monkeypatch, caplog, patch_qdrant_and_store
):
    _, store = patch_qdrant_and_store

    async def none_get(aid):
        return None

    monkeypatch.setattr(
        "app.repositories.article_repository."
        "ArticleRepository.get_article_by_id",
        none_get,
    )
    service = ArticleVectorService()
    await service.add_article(uuid.uuid4())
    assert "not found or has no summary" in caplog.text
