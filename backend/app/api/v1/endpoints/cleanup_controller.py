"""
Article Cleanup Controller

API endpoints for managing article cleanup operations.
"""

from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.models import User
from app.services.article_cleanup_service import ArticleCleanupService

router = APIRouter(prefix="/cleanup", tags=["cleanup"])
logger = get_logger(__name__)


class CleanupRequest(BaseModel):
    """Request model for article cleanup."""

    days: int = Field(
        default=180,
        ge=1,
        le=3650,
        description="Delete articles older than this many days",
    )
    batch_size: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Number of articles to process in each batch",
    )
    dry_run: bool = Field(
        default=True,
        description="If true, only simulate the cleanup without actually deleting",
    )


class CleanupStats(BaseModel):
    """Response model for cleanup statistics."""

    articles_processed: int
    articles_deleted: int
    entities_deleted: int
    keyword_links_deleted: int
    matches_deleted: int
    vector_store_deletions: int
    errors: int
    cutoff_date: str


@router.post("/run", response_model=CleanupStats)
async def run_cleanup(
    request: CleanupRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_authenticated_user),
):
    """
    Run article cleanup operation.

    Args:
        request: Cleanup configuration
        background_tasks: FastAPI background tasks
        current_user: Authenticated user (must be superuser)

    Returns:
        Cleanup statistics if not running in background
    """
    if not current_user.is_superuser:
        logger.warning(
            f"Unauthorized cleanup attempt by user {current_user.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )

    logger.info(
        f"Article cleanup requested by user {current_user.id}: "
        f"days={request.days}, batch_size={request.batch_size}, dry_run={request.dry_run}"
    )

    try:
        cleanup_service = ArticleCleanupService()

        # For non-dry runs or large operations, run in background
        if not request.dry_run or request.days > 365:
            background_tasks.add_task(
                cleanup_service.cleanup_articles_older_than_days,
                request.days,
                request.batch_size,
                request.dry_run,
            )
            return CleanupStats(
                articles_processed=0,
                articles_deleted=0,
                entities_deleted=0,
                keyword_links_deleted=0,
                matches_deleted=0,
                vector_store_deletions=0,
                errors=0,
                cutoff_date="Background task started",
            )
        else:
            # For dry runs and smaller operations, run synchronously
            stats = await cleanup_service.cleanup_articles_older_than_days(
                days=request.days,
                batch_size=request.batch_size,
                dry_run=request.dry_run,
            )
            return CleanupStats(**stats)

    except Exception as e:
        logger.error(f"Error running cleanup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to run cleanup operation",
        )
