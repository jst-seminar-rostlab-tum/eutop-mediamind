from typing import Optional, Sequence, List
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.models import Article, Keyword, User
from app.repositories.keyword_repository import KeywordRepository

router = APIRouter(prefix="/keywords", tags=["keywords"])

logger = get_logger(__name__)


@router.get("")
async def get_keywords_by_topic_id(
    topic_id: UUID,
    current_user: User = Depends(get_authenticated_user)
) -> List[Keyword]:
    """
    Get keywords by topic ID.
    """
    keywords: List[Keyword] = await KeywordRepository.get_keywords_by_topic(topic_id, current_user)
    return keywords

@router.post("")
async def create_keyword_by_topic_id(
    topic_id: UUID,
    keyword_name: str,
    current_user: User = Depends(get_authenticated_user)
) -> Keyword:
    """
    Create a keyword by topic ID.
    """
    keyword: Keyword = await KeywordRepository.create_keyword_by_topic(topic_id, keyword_name, current_user)
    return keyword


@router.post("/assign-keywords-to-articles")
async def assign_keywords_to_articles(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_authenticated_user),
    page_size: int = 100,
    score_threshold: float = 0.3
):
    """
    Assign keywords to articles in the background.
    """
    if not current_user.is_superuser:
        logger.warning(f"Unauthorized access attempt by user {current_user.id}")
        return {"message": "You do not have permission to perform this action."}

    background_tasks.add_task(KeywordRepository.assign_articles_to_keywords, page_size, score_threshold)
    return {"message": "Keywords are being assigned to articles in the background."}