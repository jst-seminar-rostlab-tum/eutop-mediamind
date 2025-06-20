from fastapi import APIRouter, BackgroundTasks, Depends

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.models import User
from app.services.article_summary_service import ArticleSummaryService
from app.services.pdf_service import PDFService
from app.repositories.search_profile_repository import get_by_id


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
    # Hardcoded search profile UUID
    search_profile_id = "e8ee904c-52b1-40b8-9f1f-5acddafba4b7"
    search_profile = await get_by_id(search_profile_id)
    pdf_bytes = await PDFService.create_sample_pdf(search_profile)

    with open("output.pdf", "wb") as f:
        f.write(pdf_bytes)