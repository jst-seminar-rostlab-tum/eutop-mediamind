from typing import List
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.core.service import get_article_matching_service
from app.models import Match, User
from app.repositories.match_repository import MatchRepository
from app.services.article_matching_service import ArticleMatchingService

router = APIRouter(prefix="/matches", tags=["matches"])

logger = get_logger(__name__)


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


@router.post("/create-matches/{search_profile_id}")
async def create_matches_for_search_profile(
    search_profile_id: UUID,
    background_tasks: BackgroundTasks,
    ams: ArticleMatchingService = Depends(get_article_matching_service),
):
    """
    Create matches for a specific search profile in the background.
    """

    background_tasks.add_task(
        ams.process_matching_for_search_profile, search_profile_id
    )
    return {
        "message": "Matches are being created "
        "for the search profile in the background."
    }
