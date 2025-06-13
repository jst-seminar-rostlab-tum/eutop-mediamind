from sentence_transformers import SentenceTransformer

from backend.app.core.db import get_qdrant_connection
from backend.app.core.logger import get_logger

logger = get_logger(__name__)


def index_and_query_articles():
    client = get_qdrant_connection()
    model = SentenceTransformer("all-MiniLM-L6-v2")

    keywords = ["climate change", "artificial intelligence"]
    articles = [
        {"id": 1, "text": "The rise of AI in modern technology"},
        {"id": 2, "text": "Climate change and its global impact"},
    ]

    vectors = [model.encode(article["text"]) for article in articles]
    points = [
        {"id": article["id"], "vector": vector.tolist(), "payload": article}
        for article, vector in zip(articles, vectors)
    ]

    client.upsert(
        collection_name="news_articles",
        points=points,
    )

    for keyword in keywords:
        keyword_vector = model.encode(keyword)
        matches = client.query_points(
            collection_name="news_articles",
            query_vector=keyword_vector.tolist(),
            limit=5,
        )
        for match in matches:
            logger.info(
                f"Keyword: {keyword} matched Article ID {match.id} "
                f"with score {match.score}"
            )
