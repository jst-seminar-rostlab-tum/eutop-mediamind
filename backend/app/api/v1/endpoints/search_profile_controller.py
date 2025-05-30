from http.client import HTTPException
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from app.core.dependencies import get_current_user
from app.schemas.articles_schemas import (
    ArticleOverviewResponse,
    MatchDetailResponse,
)
from app.schemas.match_schemas import MatchFeedbackRequest
from app.schemas.request_response import FeedbackResponse
from app.schemas.search_profile_schemas import (
    SearchProfileDetailResponse,
    SearchProfileUpdateRequest,
)
from app.services.search_profiles_service import SearchProfiles

router = APIRouter(
    prefix="/search-profiles",
    tags=["search-profiles"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[SearchProfileDetailResponse])
async def get_available_search_profiles(
    current_user=Depends(get_current_user),
):
    return await SearchProfiles.get_available_search_profiles(current_user)


@router.get("/{profile_id}", response_model=SearchProfileDetailResponse)
async def get_search_profile(
    profile_id: UUID, current_user=Depends(get_current_user)
):
    return SearchProfiles.get_search_profile(profile_id, current_user)


@router.put("/{profile_id}")
async def update_search_profile(
    profile_id: UUID,
    request: SearchProfileUpdateRequest,
    current_user=Depends(get_current_user),
):
    return await SearchProfiles.update_search_profile(
        profile_id, request, current_user
    )


@router.get("/{profile_id}/overview", response_model=ArticleOverviewResponse)
async def get_profile_overview(profile_id: UUID):
    return await SearchProfiles.get_article_overview(profile_id)


@router.get(
    "/{profile_id}/article/{match_id}", response_model=MatchDetailResponse
)
async def get_match_detail(profile_id: UUID, match_id: UUID):
    return await SearchProfiles.get_match_detail(profile_id, match_id)


@router.put("/{profile_id}/article/{match_id}")
async def update_match_feedback(
    profile_id: UUID,
    match_id: UUID,
    feedback: MatchFeedbackRequest,
):
    success = await SearchProfiles.update_match_feedback(
        profile_id, match_id, feedback
    )
    if not success:
        raise HTTPException(
            status=status.HTTP_404_NOT_FOUND,
            detail="Match or profile not found or feedback update failed",
        )
    return FeedbackResponse(status="success")
