"""
NOTE:
This is just a testing controller for vector store.
Once we have a proper scheduler, we can remove this controller.
"""

from fastapi import APIRouter, BackgroundTasks

from app.core.logger import get_logger
from app.services.article_vector_service import ArticleVectorService

router = APIRouter(prefix="/vector-store", tags=["vector-store"])

logger = get_logger(__name__)


@router.post("/add-articles")
async def add_articles_to_vector_store(
    background_tasks: BackgroundTasks, page_size: int = 100
):
    """
    Add a list of articles to the vector store.
    """
    vector_service = ArticleVectorService()
    background_tasks.add_task(
        vector_service.index_summarized_articles_to_vector_store, page_size
    )
    return {"message": "Articles are being added to the vector store."}
