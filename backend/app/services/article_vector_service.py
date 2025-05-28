from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, SparseVectorParams, VectorParams
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode

from app.core.config import configs


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




if __name__ == "__main__":
    service = ArticleVectorService()
    print("ArticleVectorService initialized with OpenAI embeddings and sparse embeddings.")
    service.create_collection("my_documents")
    res = service.get_list_of_collections()
    print(res)
    service.delete_collection("my_documents")
    res = service.get_list_of_collections()

    print(res)
    # You can add more functionality to test the service here.