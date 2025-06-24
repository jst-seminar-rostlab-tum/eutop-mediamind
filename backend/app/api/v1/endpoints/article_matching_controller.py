"""
NOTE:
This is just a testing controller for article matching.
Once we have a proper scheduler, we can remove this controller.
"""

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.core.service import get_article_matching_service
from app.services.article_matching_service import ArticleMatchingService

router = APIRouter(
    prefix="/article-matching",
    tags=["article-matching"],
    dependencies=[Depends(get_authenticated_user)],
)

logger = get_logger(__name__)


@router.post("/")
async def create_article_matching(
    background_tasks: BackgroundTasks,
    ams: ArticleMatchingService = Depends(get_article_matching_service),
):
    background_tasks.add_task(ams.run)
    return {"message": "Article matching started in the background."}
