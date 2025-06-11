from fastapi import APIRouter, BackgroundTasks, Depends

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.models import User
from app.repositories.article_repository import *
from app.services.article_vector_service import ArticleVectorService

router = APIRouter(prefix="/vector-store", tags=["vector-store"])

logger = get_logger(__name__)

def get_vector_service() -> ArticleVectorService:
    return ArticleVectorService()

@router.get("/collections")
async def get_vector_store_collections(
    current_user: User = Depends(get_authenticated_user),
    vector_service: ArticleVectorService = Depends(get_vector_service),
):
    if not current_user.is_superuser:
        logger.warning(f"Unauthorized access attempt by user {current_user.id}")
        return {"message": "You do not have permission to perform this action."}
    return vector_service.get_list_of_collections()

@router.delete("/collections/{collection_name}")
async def delete_vector_store_collection(
    collection_name: str,
    current_user: User = Depends(get_authenticated_user),
    vector_service: ArticleVectorService = Depends(get_vector_service),
):
    if not current_user.is_superuser:
        logger.warning(f"Unauthorized access attempt by user {current_user.id}")
        return {"message": "You do not have permission to perform this action."}
    vector_service.delete_collection(collection_name)
    return {"message": f"Collection '{collection_name}' deleted successfully."}


@router.post("/add-articles")
async def add_articles_to_vector_store(
    background_tasks: BackgroundTasks,
    page_size: int = 100,
    current_user: User = Depends(get_authenticated_user),
    vector_service: ArticleVectorService = Depends(get_vector_service),
):
    """
    Add a list of articles to the vector store.
    """
    if not current_user.is_superuser:
        logger.warning(f"Unauthorized access attempt by user {current_user.id}")
        return {"message": "You do not have permission to perform this action."}
    background_tasks.add_task(vector_service.index_summarized_articles_to_vector_store, page_size)
    return {"message": "Articles are being added to the vector store."}