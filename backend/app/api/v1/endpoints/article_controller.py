from fastapi import APIRouter, Depends

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.repositories.article_repository import *
from app.services.article_summary_service import summarize_text

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

    summary = summarize_text(article.content)

    return summary


@router.get("", response_model=list[Article])
async def list_articles(
    limit: int = 100, offset: int = 0, set_of: int = 0
):
    """
    List articles with optional pagination and batch processing.
    """
    articles = await ArticleRepository.list_articles(limit, offset, set_of)
    return articles
