from typing import Optional, Sequence
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.models import Article, Keyword
from app.repositories.keyword_repository import KeywordRepository

router = APIRouter(prefix="/keywords", tags=["keywords"])

logger = get_logger(__name__)


@router.get("/list")
async def get_keywords_list(
    limit: int = 100, offset: int = 0
) -> Sequence[Keyword]:
    """
    Retrieve a list of keywords with pagination.
    """

    keywords = await KeywordRepository.list_keywords(
        limit=limit, offset=offset
    )
    return keywords


@router.post("/add")
async def add_keyword(keyword: str) -> Keyword:
    """
    Add a new keyword to the database.
    """
    new_keyword = await KeywordRepository.add_keyword(keyword)
    return new_keyword


@router.get("/{keyword_id}/most_similar_articles")
async def get_most_similar_articles(
    keyword_id: UUID, score_threshold: float = 0.3
) -> Sequence[Article]:
    """
    Retrieve the most similar articles for a given keyword.
    """
    articles = await KeywordRepository.get_most_similar_articles(
        keyword_id, score_threshold=score_threshold
    )
    return articles


@router.get("/assign-articles")
async def assign_articles_to_vector_store(background_tasks: BackgroundTasks):
    """
    Assign all articles to the vector store in the background.
    """
    # background_tasks.add_task(KeywordRepository.assign_articles_to_keywords)
    await KeywordRepository.assign_articles_to_keywords()
    return {"message": "All articles are being assigned to the vector store."}
