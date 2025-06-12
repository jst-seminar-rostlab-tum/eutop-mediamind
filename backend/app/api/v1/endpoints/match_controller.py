from typing import List
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.models import Match, User
from app.repositories.match_repository import MatchRepository
from app.services.matching_service import ArticleMatchingService

router = APIRouter(prefix="/matches", tags=["matches"])

logger = get_logger(__name__)


@router.post("/create-matches")
async def create_matches(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_authenticated_user),
    page_size: int = 100,
):
    """
    Create matches for articles in the background.
    """
    if not current_user.is_superuser:
        logger.warning(
            f"Unauthorized access attempt by user {current_user.id}"
        )
        return {
            "message": "You do not have permission to perform this action."
        }

    background_tasks.add_task(ArticleMatchingService.run, page_size)
    return {"message": "Matches are being created in the background."}


@router.get("")
async def get_matches_by_search_profile(
    search_profile_id: UUID,
    current_user: User = Depends(get_authenticated_user),
) -> List[Match]:
    """
    Get matches by search profile ID.
    """
    matches: List[Match] = await MatchRepository.get_matches_by_search_profile(
        search_profile_id, current_user
    )
    return matches
