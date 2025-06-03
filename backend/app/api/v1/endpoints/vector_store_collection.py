from fastapi import APIRouter, Depends, BackgroundTasks

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.repositories.article_repository import *
from app.services.article_vector_service import ArticleVectorService

router = APIRouter(prefix="/vector-store", tags=["vector-store"])

logger = get_logger(__name__)

@router.get("/collections")
async def get_vector_store_collections():
    """
    Retrieve a list of all vector store collections.
    """
    vector_service = ArticleVectorService()
    collections = vector_service.get_list_of_collections()
    return collections

@router.post("/collections")
async def create_vector_store_collection(collection_name: str):
    """
    Create a new vector store collection with the specified name.
    """
    vector_service = ArticleVectorService()
    vector_service.create_collection(collection_name)
    return {"message": f"Collection '{collection_name}' created successfully."}

@router.delete("/collections/{collection_name}")
async def delete_vector_store_collection(collection_name: str):
    """
    Delete a specific vector store collection by its name.
    """
    vector_service = ArticleVectorService()
    vector_service.delete_collection(collection_name)
    return {"message": f"Collection '{collection_name}' deleted successfully."}