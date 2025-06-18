from fastapi import APIRouter, BackgroundTasks, Depends

from app.core.auth import get_authenticated_user
from app.core.db import get_vector_service
from app.core.logger import get_logger
from app.models import User
from app.services.article_vector_service import ArticleVectorService

router = APIRouter(prefix="/vector-store", tags=["vector-store"])

logger = get_logger(__name__)


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
        logger.warning(
            f"Unauthorized access attempt by user {current_user.id}"
        )
        return {
            "message": "You do not have permission to perform this action."
        }
    background_tasks.add_task(
        vector_service.index_summarized_articles_to_vector_store, page_size
    )
    return {"message": "Articles are being added to the vector store."}
