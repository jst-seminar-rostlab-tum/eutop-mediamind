from fastapi import APIRouter, BackgroundTasks, Depends

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.models import User
from app.repositories.article_repository import *
from app.services.article_summary_service import ArticleSummaryService

router = APIRouter(prefix="/articles", tags=["articles"])

logger = get_logger(__name__)

@router.post("/summarize-all")
async def summarize_all_articles(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_authenticated_user),
    page_size: int = 100,
):
    """
    Summarize all articles in the database.
    """
    if not current_user.is_superuser:
        logger.warning(f"Unauthorized access attempt by user {current_user.id}")
        return {"message": "You do not have permission to perform this action."}
    logger.info("Summarizing all articles")
    background_tasks.add_task(ArticleSummaryService.run, page_size)
    return {"message": "Summarization started in the background."}