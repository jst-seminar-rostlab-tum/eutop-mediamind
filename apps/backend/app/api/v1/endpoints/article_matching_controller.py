"""
NOTE:
This is just a testing controller for article matching.
Once we have a proper scheduler, we can remove this controller.
"""

from fastapi import APIRouter, BackgroundTasks, Depends

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
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
):
    ams = ArticleMatchingService()
    background_tasks.add_task(ams.run)
    return {"message": "Article matching started in the background."}
