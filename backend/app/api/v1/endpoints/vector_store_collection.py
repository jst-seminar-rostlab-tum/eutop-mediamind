from fastapi import APIRouter, Depends, BackgroundTasks

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.repositories.article_repository import *
from app.services.article_vector_service import ArticleVectorService

router = APIRouter(prefix="/vector-store", tags=["vector-store"])

logger = get_logger(__name__)

vector_service = ArticleVectorService()

@router.get("/collections")
async def get_vector_store_collections():
    """
    Retrieve a list of all vector store collections.
    """

    collections = vector_service.get_list_of_collections()
    return collections

@router.post("/collections")
async def create_vector_store_collection(collection_name: str):
    """
    Create a new vector store collection with the specified name.
    """

    vector_service.create_collection(collection_name)
    return {"message": f"Collection '{collection_name}' created successfully."}

@router.delete("/collections/{collection_name}")
async def delete_vector_store_collection(collection_name: str):
    """
    Delete a specific vector store collection by its name.
    """

    vector_service.delete_collection(collection_name)
    return {"message": f"Collection '{collection_name}' deleted successfully."}


@router.get("/add-article")
async def add_article_to_vector_store(
    article_id: UUID, background_tasks: BackgroundTasks
):
    """
    Add an article to the vector store in the background.
    """
    await vector_service.add_article(article_id)
    return {"message": f"Article {article_id} is being added to the vector store."}

@router.post("/add-articles")
async def add_articles_to_vector_store(
    background_tasks: BackgroundTasks
):
    """
    Add all articles without summaries to the vector store in the background.
    """
    background_tasks.add_task(vector_service.run_save_articles_to_vector_store)
    return {"message": "All articles without summaries are being added to the vector store."}


@router.get("/search-similarity")
async def search_vector_store_by_similarity(
    query: str, score_threshold: float = 0.3
):
    """
    Search the vector store for articles similar to the query.
    """
    results = await vector_service.retrieve_by_similarity(query, score_threshold)
    return results

