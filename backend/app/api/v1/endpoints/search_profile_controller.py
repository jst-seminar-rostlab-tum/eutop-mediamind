from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.models.user import User
from app.schemas.articles_schemas import (
    ArticleOverviewResponse,
    MatchDetailResponse,
)
from app.schemas.match_schemas import MatchFeedbackRequest
from app.schemas.report_schemas import ReportListResponse, ReportRead
from app.schemas.request_response import FeedbackResponse, MatchFilterRequest
from app.schemas.search_profile_schemas import (
    KeywordSuggestionResponse,
    SearchProfileCreateRequest,
    SearchProfileDetailResponse,
    SearchProfileUpdateRequest,
)
from app.schemas.user_schema import UserEntity
from app.services.report_service import ReportService
from app.services.search_profiles_service import SearchProfileService

router = APIRouter(
    prefix="/search-profiles",
    tags=["search-profiles"],
    dependencies=[Depends(get_authenticated_user)],
)

logger = get_logger(__name__)


@router.get("", response_model=List[SearchProfileDetailResponse])
async def get_available_search_profiles(
    current_user: UserEntity = Depends(get_authenticated_user),
) -> List[SearchProfileDetailResponse]:
    """
    Retrieve all search profiles available to the current user.
    """
    return await SearchProfileService.get_available_search_profiles(
        current_user
    )


@router.post(
    "/keywords/suggestions",
    response_model=KeywordSuggestionResponse,
)
async def get_keyword_suggestions(
    keywords: List[str],
    current_user: User = Depends(get_authenticated_user),
) -> KeywordSuggestionResponse:
    """
    Return keyword suggestions based on a list of input keywords.
    """
    return await SearchProfileService.get_keyword_suggestions(
        current_user, keywords
    )


@router.get(
    "/{search_profile_id}",
    response_model=SearchProfileDetailResponse,
)
async def get_search_profile(
    search_profile_id: UUID,
    current_user: UserEntity = Depends(get_authenticated_user),
) -> SearchProfileDetailResponse:
    """
    Retrieve a specific search profile by its UUID.
    """
    profile = await SearchProfileService.get_extended_by_id(
        search_profile_id, current_user
    )
    if not profile:
        logger.warning("Search profile %s not found", search_profile_id)
        raise HTTPException(
            status_code=404,
            detail="Search profile not found",
        )

    return profile


@router.post(
    "/{search_profile_id}/matches", response_model=ArticleOverviewResponse
)
async def get_search_profile_overview(
    search_profile_id: UUID,
    request: MatchFilterRequest,
    current_user: User = Depends(get_authenticated_user),
):
    return await SearchProfileService.get_article_matches(
        search_profile_id=search_profile_id,
        request=request,
        current_user=current_user,
    )
    """
    Retrieve an overview of articles for a given search profile.
    """


@router.get(
    "/{search_profile_id}/article/{match_id}",
    response_model=MatchDetailResponse,
)
async def get_match_detail(
    search_profile_id: UUID,
    match_id: UUID,
    current_user: User = Depends(get_authenticated_user),
) -> MatchDetailResponse:
    """
    Retrieve detailed match information for a specific article match.
    """
    detail = await SearchProfileService.get_match_detail(
        search_profile_id, match_id, current_user
    )
    if not detail:
        logger.warning(
            f"Match detail for profile {search_profile_id}, "
            f"match {match_id} not found",
            search_profile_id,
            match_id,
        )
        raise HTTPException(
            status_code=404,
            detail="Match not found",
        )

    return detail


@router.post("", response_model=SearchProfileDetailResponse)
async def create_search_profile(
    profile_data: SearchProfileCreateRequest,
    current_user: UserEntity = Depends(get_authenticated_user),
) -> SearchProfileDetailResponse:
    """
    Create a new search profile for the current user.
    """
    return await SearchProfileService.create_search_profile(
        profile_data, current_user
    )


@router.put(
    "/{search_profile_id}",
    response_model=SearchProfileDetailResponse,
)
async def update_search_profile(
    search_profile_id: UUID,
    update_data: SearchProfileUpdateRequest,
    current_user: UserEntity = Depends(get_authenticated_user),
) -> SearchProfileDetailResponse:
    """
    Update an existing search profile by its UUID.
    """
    return await SearchProfileService.update_search_profile(
        search_profile_id, update_data, current_user
    )


@router.put(
    "/{search_profile_id}/article/{match_id}",
    response_model=FeedbackResponse,
)
async def update_match_feedback(
    search_profile_id: UUID,
    match_id: UUID,
    feedback: MatchFeedbackRequest,
) -> FeedbackResponse:
    """
    Update feedback for a specific match within a search profile.
    """
    success = await SearchProfileService.update_match_feedback(
        search_profile_id, match_id, feedback
    )
    if not success:
        logger.error(
            f"Failed to update feedback for profile {search_profile_id}, "
            f"match {match_id}"
        )
        raise HTTPException(
            status_code=404,
            detail="Match not found or feedback update failed",
        )

    return FeedbackResponse(status="success")


@router.get("/{search_profile_id}/reports", response_model=ReportListResponse)
async def get_reports(
    search_profile_id: UUID,
    current_user: User = Depends(get_authenticated_user),
):
    profile = await SearchProfileService.get_extended_by_id(
        search_profile_id, current_user
    )
    if profile is None:
        raise HTTPException(status_code=404, detail="Search profile not found")

    reports = await ReportService.get_reports_by_search_profile(
        search_profile_id
    )
    if not reports:
        raise HTTPException(
            status_code=404, detail="No reports found for this profile"
        )

    reports_pydantic = [
        ReportRead.model_validate(r, from_attributes=True) for r in reports
    ]
    return ReportListResponse(reports=reports_pydantic)
