from typing import List
import uuid

from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from langchain_core.documents import Document
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, SparseVectorParams, VectorParams
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from langchain.indexes import SQLRecordManager

from app.core.config import configs
from app.models import Article


class ArticleVectorService:

    def __init__(self):
        self._embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=configs.OPENAI_API_KEY)
        self._sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
        self.collection_name = "article_vectors"


        self._qdrant_client = QdrantClient(
            url=configs.QDRANT_HOST,
            api_key=configs.QDRANT_API_KEY,
            prefer_grpc=True
        )

        self.create_collection(self.collection_name)
        self.vector_store: QdrantVectorStore = self.init_vector_store(collection_name=self.collection_name)

    def init_vector_store(self, collection_name: str):
        """
        Initialize the Qdrant vector store with the specified collection name.
        """
        return QdrantVectorStore(
            client=self._qdrant_client,
            collection_name=collection_name,
            embedding=self._embeddings,
            sparse_embedding=self._sparse_embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
            vector_name="dense",
            sparse_vector_name="sparse"
        )

    def create_collection(self, collection_name: str):
        """
        Create a Qdrant collection for storing article vectors.
        """
        if not self._qdrant_client.collection_exists(collection_name):
            self._qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config={"dense": VectorParams(size=3072, distance=Distance.COSINE)},
                sparse_vectors_config={
                    "sparse": SparseVectorParams(index=models.SparseIndexParams(on_disk=False))
                },
            )

    def delete_collection(self, collection_name: str):
        """
        Delete a Qdrant collection.
        """
        if self._qdrant_client.collection_exists(collection_name):
            self._qdrant_client.delete_collection(collection_name=collection_name)

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
        documents = [Document(page_content=article.summary,
                              metadata={'id': article.id,
                                        'subscription_id': article.subscription_id,}
                              )
                     for article in articles]

        uuids = [article.id for article in articles]

        self.vector_store.add_documents(documents=documents, ids=uuids)

    def retrieve_by_similarity(self, query: str, score_threshold: float = 0.3) -> list[tuple[Document, float]]:
        """
        Retrieve documents from the vector store based on similarity to the query.
        Args:
            query (str): The query string to search for.
            score_threshold (float): Minimum score threshold for results.

        Returns:
            List[Document]: List of documents that match the query.
        """

        return self.vector_store.similarity_search_with_score(query=query, score_threshold=score_threshold)


if __name__ == "__main__":
    service = ArticleVectorService()
    print("ArticleVectorService initialized with OpenAI embeddings and sparse embeddings.")
    service.create_collection("my_documents")
    res = service.get_list_of_collections()
    print(res)
    service.delete_collection("my_documents")
    res = service.get_list_of_collections()

    test_articles = [
        Article(id=str(uuid.uuid4()), title="Test Article 1", content="This is the content of test article 1.",
                url="http://example.com/article1", author="Author 1", published_at="2023-10-01T00:00:00Z",
                language="en", category="test", summary="This is a summary of test article 1.",
                subscription_id="sub_123"),
        Article(id=str(uuid.uuid4()), title="Test Article 2", content="This is the content of test article 2.",
                url="http://example.com/article2", author="Author 2", published_at="2023-10-02T00:00:00Z",
                language="en", category="test", summary="This is a summary of test article 2.",
                subscription_id="sub_456")
    ]

    #service.add_articles(test_articles)
    res = service.retrieve_by_similarity("test article")
    print(res)
    # You can add more functionality to test the service here.