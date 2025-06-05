import asyncio
import uuid
from typing import List, Optional

from langchain.indexes import SQLRecordManager
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import (
    Distance,
    SparseVectorParams,
    VectorParams,
)
from starlette.concurrency import run_in_threadpool

from app.core.config import configs
from app.models import Article
from app.repositories.article_repository import ArticleRepository


class ArticleVectorService:

    def __init__(self):
        self._embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large", api_key=configs.OPENAI_API_KEY
        )
        self._sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
        self.collection_name = "article_vectors"

        self._qdrant_client = QdrantClient(
            url=configs.QDRANT_HOST, api_key=configs.QDRANT_API_KEY
        )

        self._ensure_collection(self.collection_name)

        self.vector_store: QdrantVectorStore = QdrantVectorStore(
            client=self._qdrant_client,
            collection_name=self.collection_name,
            embedding=self._embeddings,
            sparse_embedding=self._sparse_embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
            vector_name="dense",
            sparse_vector_name="sparse",
        )

    def _ensure_collection(self, collection_name: str) -> None:

        try:
            if not self._qdrant_client.collection_exists(
                collection_name=collection_name
            ):
                self._qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config={
                        "dense": VectorParams(
                            size=3072, distance=Distance.COSINE
                        )
                    },
                    sparse_vectors_config={
                        "sparse": SparseVectorParams(
                            index=models.SparseIndexParams(on_disk=False)
                        )
                    },
                )
        except Exception as e:
            pass

    def create_collection(self, collection_name: str):
        """
        Create a Qdrant collection for storing article vectors.
        """
        if not self._qdrant_client.collection_exists(collection_name):
            self._qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    "dense": VectorParams(size=3072, distance=Distance.COSINE)
                },
                sparse_vectors_config={
                    "sparse": SparseVectorParams(
                        index=models.SparseIndexParams(on_disk=False)
                    )
                },
            )

    def delete_collection(self, collection_name: str):
        """
        Delete a Qdrant collection.
        """
        if self._qdrant_client.collection_exists(collection_name):
            self._qdrant_client.delete_collection(
                collection_name=collection_name
            )

    def get_list_of_collections(self):
        """
        Get a list of all collections in Qdrant.
        """
        return self._qdrant_client.get_collections()

    def add_articles(self, articles: List[Article]) -> None:
        """
        Add a list of articles to the vector store.
        Args:
            articles(List[Article]): List of Article objects to be added to the vector store.

        Returns:

        """
        documents = [
            Document(
                page_content=article.summary,
                metadata={
                    "id": article.id,
                    "subscription_id": article.subscription_id,
                },
            )
            for article in articles
        ]

        uuids = [article.id for article in articles]

        self.vector_store.add_documents(documents=documents, ids=uuids)

    async def retrieve_by_similarity(
        self, query: str, score_threshold: float = 0.3
    ) -> list[tuple[Document, float]]:
        """
        Retrieve documents from the vector store based on similarity to the query.
        Args:
            query (str): The query string to search for.
            score_threshold (float): Minimum score threshold for results.

        Returns:
            List[Document]: List of documents that match the query.
        """

        return self.vector_store.similarity_search_with_score(
            query=query, score_threshold=score_threshold
        )

    async def run_save_articles_to_vector_store(
        self, page_size: int = 100
    ) -> None:
        """
        Run the functionality to read articles from the database and add them to the vector store.
        """
        page = 0
        while True:
            offset = page * page_size
            # 1) Asynchron alle Artikel der Seite abrufen
            articles = await ArticleRepository.list_articles_with_summary(
                limit=page_size, offset=offset
            )
            if not articles:
                break

            print(
                f"--> Processing page {page} with {len(articles)} articles..."
            )

            # 2) Nur Artikel mit nicht-leerer summary auswählen
            documents = []
            ids = []
            for article in articles:
                if article.summary and article.summary.strip():
                    documents.append(
                        Document(
                            page_content=article.summary,
                            metadata={
                                "id": str(article.id),
                                "subscription_id": str(
                                    article.subscription_id
                                ),
                                "title": article.title,
                            },
                        )
                    )
                    ids.append(str(article.id))

            print(
                f"--> Found {len(documents)} articles with non-empty summaries on page {page}."
            )

            # 3) Falls Dokumente vorhanden sind, füge sie asynchron in Qdrant ein
            if documents:
                self.vector_store.add_documents(documents=documents, ids=ids)

            page += 1


async def add_article(self, article_id: uuid.UUID) -> None:
    article: Optional[Article] = await ArticleRepository.get_article_by_id(
        article_id
    )
    print(article)
    if not article or not article.summary or not article.summary.strip():
        return

    document = Document(
        page_content=article.summary,
        metadata={
            "id": str(article.id),
            "subscription_id": str(article.subscription_id),
            "title": article.title,
        },
    )

    self.vector_store.add_documents(
        documents=[document], ids=[str(article.id)]
    )


def test_run_():

    service = ArticleVectorService()
    print(
        "ArticleVectorService initialized with OpenAI embeddings and sparse embeddings."
    )
    service.create_collection("my_documents")
    res = service.get_list_of_collections()
    print(res)
    service.delete_collection("my_documents")
    res = service.get_list_of_collections()

    test_articles = [
        Article(
            id="3d8b0ee9-3f55-445e-b95b-d9cdca9477fe",
            title="Test Article 1",
            content="This is the content of test article 1.",
            url="http://example.com/article1",
            author="Author 1",
            published_at="2023-10-01T00:00:00Z",
            language="en",
            category="test",
            summary="This is a summary of test article 1.",
            subscription_id=str(uuid.uuid4()),
        ),
        Article(
            id="8e4790c7-e464-47de-8e5d-0aee2da78948",
            title="Test Article 2",
            content="This is the content of test article 2.",
            url="http://example.com/article2",
            author="Author 2",
            published_at="2023-10-02T00:00:00Z",
            language="en",
            category="test",
            summary="This is a summary of test article 2.",
            subscription_id=str(uuid.uuid4()),
        ),
    ]

    service.add_articles(test_articles)
    res = service.retrieve_by_similarity("test article")
    print(res)
    # You can add more functionality to test the service here.

    """
    for i in test_articles:
        ArticleRepository.create_article(i)

    res = ArticleRepository.list_articles()
    """
    print(res)


import asyncio
from uuid import UUID

from sqlmodel import Session

from app.core.db import engine
from app.models.article import Article
from app.repositories.article_repository import ArticleRepository

"""

from uuid import UUID
from app.models.article import Article
from app.repositories.article_repository import ArticleRepository

def main():
    # 1) Neuen Artikel anlegen
    art = Article(
        id=UUID("3d8b0ee9-3f55-445e-b95b-d9cdca9477fe"),
        title="Test",
        content="...",
        url="http://...",
        author="Author",
        published_at="2023-10-01T00:00:00Z",
        language="en",
        category="test",
        summary="",
        subscription_id=None

    )

    # Artikel erstellen
    created = ArticleRepository.create_article(art)
    print("Created:", created)

    # Alle Artikel abrufen
    all_articles = ArticleRepository.list_articles()
    print("All:", all_articles)

    # Einzelnen Artikel holen
    fetched = ArticleRepository.get_article_by_id(art.id)
    print("Fetched:", fetched)

    # Artikel updaten
    art.title = "Updated Title"
    updated = ArticleRepository.update_article(art)
    print("Updated:", updated)
"""
if __name__ == "__main__":
    test_run_()
