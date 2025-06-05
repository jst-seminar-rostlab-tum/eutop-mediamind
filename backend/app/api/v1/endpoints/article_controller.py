from fastapi import APIRouter, BackgroundTasks, Depends

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.repositories.article_repository import *
from app.services.article_summary_service import ArticleSummaryService

router = APIRouter(prefix="/articles", tags=["articles"])

logger = get_logger(__name__)


@router.get("/{article_id}", response_model=Article)
async def get_article(article_id: UUID):
    """
    Retrieve a specific article by its ID.
    """

    article = await ArticleRepository.get_article_by_id(article_id)

    return article


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


@router.post("/summarize_all")
async def summarize_all_articles(
    background_tasks: BackgroundTasks, page_size: int = 100
):
    """
    Startet die Batch-Zusammenfassung im Hintergrund. Gibt sofort eine Bestätigung zurück.
    """
    # 1) Registrierung des Background-Tasks
    background_tasks.add_task(ArticleSummaryService.run, page_size)

    # 2) Sofortige Response
    return {
        "detail": "Batch summarization wurde gestartet. Läuft im Hintergrund."
    }


@router.get("", response_model=list[Article])
async def list_articles(limit: int = 100, offset: int = 0, set_of: int = 0):
    """
    List articles with optional pagination and batch processing.
    """
    articles = await ArticleRepository.list_articles(limit, offset, set_of)
    return articles
