from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.models import User
from app.repositories.article_repository import ArticleRepository
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
        logger.warning(
            f"Unauthorized access attempt by user {current_user.id}"
        )
        return {
            "message": "You do not have permission to perform this action."
        }
    logger.info("Summarizing all articles")
    background_tasks.add_task(ArticleSummaryService.run, page_size)
    return {"message": "Summarization started in the background."}



@router.get("/{article_id}/summarize")
async def summarize_article(article_id: UUID):
    """
    Summarize the content of a specific article.
    """
    article = await ArticleRepository.get_article_by_id(article_id)
    if not article:
        return "Article not found"

    summary = ArticleSummaryService.summarize_text(article.content)

    return summary


@router.get("/{article_id}/summarize/store")
async def summarize_and_store_article(article_id: UUID):
    """
    Summarize the content of a specific article and store the summary in the database.
    """
    updated_article = await ArticleSummaryService.summarize_and_store(
        article_id
    )
    if not updated_article:
        return "Article not found or could not be summarized"

    return updated_article