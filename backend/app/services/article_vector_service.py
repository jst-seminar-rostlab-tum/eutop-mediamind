import uuid
from typing import List, Optional, Sequence

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from qdrant_client import models
from qdrant_client.http.models import (
    Distance,
    SparseVectorParams,
    VectorParams,
)

from app.core.config import configs
from app.core.db import get_qdrant_connection
from app.core.logger import get_logger
from app.models import Article
from app.repositories.article_repository import ArticleRepository

logger = get_logger(__name__)


class ArticleVectorService:
    """Service for managing article vectors in Qdrant."""

    def __init__(self):
        self._dense_embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large", api_key=configs.OPENAI_API_KEY
        )
        self._sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
        self.collection_name = configs.ARTICLE_VECTORS_COLLECTION
        self._qdrant_client = get_qdrant_connection()
        self.create_collection_safe(self.collection_name)
        self.vector_store: QdrantVectorStore = QdrantVectorStore(
            client=self._qdrant_client,
            collection_name=self.collection_name,
            embedding=self._dense_embeddings,
            sparse_embedding=self._sparse_embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
            # Use both dense and sparse vectors
            # during search for improved recall and precision
            vector_name="dense",
            # Field name in Qdrant for storing dense vectors
            sparse_vector_name="sparse",
            # Field name in Qdrant for storing sparse vectors
        )

    def create_collection_safe(self, collection_name: str) -> None:
        """
        Create a Qdrant collection for storing vectors.
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
            articles(List[Article]): Articles to index.

        """
        documents = [
            Document(
                page_content=article.summary,
                metadata={
                    "id": str(article.id),
                    "subscription_id": str(article.subscription_id),
                    "title": article.title,
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
        Retrieve query-relevant documents from the vector store.
        Args:
            query (str): The query string to search for.
            score_threshold (float): Minimum score threshold for results.

        Returns:
            List[Document]: List of documents that match the query.
        """

        return self.vector_store.similarity_search_with_score(
            query=query, score_threshold=score_threshold
        )

    async def index_summarized_articles_to_vector_store(
        self, page_size: int = 100
    ) -> None:
        """
        Run the functionality to read articles from the database and
        add them to the vector store.
        """
        page: int = 0
        offset: int = page * page_size

        articles: List[Article] = (
            await ArticleRepository.list_articles_with_summary(
                limit=page_size, offset=offset
            )
        )

        while articles:


            self.add_articles(articles)

            page += 1
            offset = page * page_size

            articles = await ArticleRepository.list_articles_with_summary(
                limit=page_size, offset=offset
            )


    async def add_article(self, article_id: uuid.UUID) -> None:
        """
        Add an article to the vector store based on its ID.
        Args:
            self: Instance of the ArticleVectorService.
            article_id: UUID of the article to be added to the vector store.

        Returns: None

        """
        article: Optional[Article] = await ArticleRepository.get_article_by_id(
            article_id
        )

        if not article or not article.summary or not article.summary.strip():
            logger.error(
                f"Article with ID {article_id} not found or has no summary."
            )
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
