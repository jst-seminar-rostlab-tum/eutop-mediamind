from fastapi import APIRouter, BackgroundTasks, Depends

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.models import User
from app.repositories.search_profile_repository import get_by_id
from app.services.article_summary_service import ArticleSummaryService
from app.services.pdf_service import PDFService

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


@router.get("/pdf")
async def trigger_pdf_creation():
    from datetime import datetime

    # TODO: Takeout this endpoint when no more design tests needed
    # Probably never :(
    # Hardcoded search profile UUID for demonstration purposes
    search_profile_id = "7ea2dacc-2e5b-457a-a26b-906b3ed562fa"
    search_profile = await get_by_id(search_profile_id)
    pdf_bytes = await PDFService.create_pdf(
        search_profile, "morning", datetime.now()
    )

    with open("output.pdf", "wb") as f:
        f.write(pdf_bytes)
