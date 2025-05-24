from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

client = QdrantClient("localhost", port=6333)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Sample-data
keywords = ["climate change", "artificial intelligence"]
articles = [
    {"id": 1, "text": "The rise of AI in modern technology"},
    {"id": 2, "text": "Climate change and its global impact"},
]

# Add article
vectors = [model.encode(article["text"]) for article in articles]
client.upsert(
    collection_name="news_articles",
    points=[
        {"id": article["id"], "vector": vector.tolist(), "payload": article}
        for article, vector in zip(articles, vectors)
    ],
)

# check similarity
for keyword in keywords:
    keyword_vector = model.encode(keyword)
    matches = client.query_points(
        collection_name="news_articles",
        query_vector=keyword_vector.tolist(),
        limit=5,
    )
    for match in matches:
        print(
            f"Keyword: {keyword} matched Article ID {match.id} with score {match.score}"
        )
