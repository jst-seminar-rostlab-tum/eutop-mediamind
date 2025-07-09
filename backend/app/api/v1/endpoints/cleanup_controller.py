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


class CleanupPreview(BaseModel):
    """Response model for cleanup preview."""

    cutoff_date: str
    articles_to_delete: int
    entities_to_delete: int
    keyword_links_to_delete: int
    matches_to_delete: int
    oldest_article_date: Optional[str]
    newest_article_date: Optional[str]


@router.get("/preview", response_model=CleanupPreview)
async def get_cleanup_preview(
    days: int = 180,
    current_user: User = Depends(get_authenticated_user),
):
    """
    Get a preview of what would be deleted in a cleanup operation.

    Args:
        days: Number of days to look back for article deletion
        current_user: Authenticated user (must be superuser)

    Returns:
        Preview of what would be deleted
    """
    if not current_user.is_superuser:
        logger.warning(
            f"Unauthorized cleanup preview attempt by user {current_user.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )

    try:
        cleanup_service = ArticleCleanupService()
        preview = await cleanup_service.get_cleanup_preview(days=days)
        return CleanupPreview(**preview)
    except Exception as e:
        logger.error(f"Error getting cleanup preview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get cleanup preview",
        )


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


@router.delete("/articles/{days}", response_model=dict)
async def delete_old_articles(
    days: int,
    current_user: User = Depends(get_authenticated_user),
    batch_size: int = 100,
):
    """
    Immediately delete articles older than specified days.

    ⚠️ WARNING: This operation cannot be undone!

    Args:
        days: Delete articles older than this many days
        current_user: Authenticated user (must be superuser)
        batch_size: Number of articles to process in each batch

    Returns:
        Confirmation message
    """
    if not current_user.is_superuser:
        logger.warning(
            f"Unauthorized article deletion attempt by user {current_user.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )

    if days < 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete articles newer than 30 days for safety reasons",
        )

    logger.warning(
        f"IMMEDIATE ARTICLE DELETION requested by user {current_user.id}: "
        f"days={days}, batch_size={batch_size}"
    )

    try:
        cleanup_service = ArticleCleanupService()
        stats = await cleanup_service.cleanup_articles_older_than_days(
            days=days, batch_size=batch_size, dry_run=False
        )

        logger.warning(
            f"Article deletion completed: {stats['articles_deleted']} articles deleted"
        )

        return {
            "message": f"Successfully deleted {stats['articles_deleted']} articles and related data",
            "stats": stats,
        }

    except Exception as e:
        logger.error(f"Error deleting articles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete articles",
        )
