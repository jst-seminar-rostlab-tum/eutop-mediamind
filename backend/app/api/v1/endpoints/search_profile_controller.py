from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.models import User
from app.schemas.articles_schemas import (
    ArticleOverviewResponse,
    MatchDetailResponse,
)
from app.schemas.match_schemas import MatchFeedbackRequest
from app.schemas.search_profile_schemas import (
    SearchProfileCreateRequest,
    SearchProfileDetailResponse,
    SearchProfileUpdateRequest,
)
from app.services.search_profiles_service import SearchProfileService

router = APIRouter(
    prefix="/search-profiles",
    tags=["search-profiles"],
    dependencies=[Depends(get_authenticated_user)],
)

logger = get_logger(__name__)


@router.get("", response_model=list[SearchProfileDetailResponse])
async def get_available_search_profiles(
    current_user=Depends(get_authenticated_user),
):
    return await SearchProfileService.get_available_search_profiles(
        current_user
    )


@router.get("/{search_profile_id}", response_model=SearchProfileDetailResponse)
async def get_search_profile(
    search_profile_id: UUID, current_user=Depends(get_authenticated_user)
):
    return await SearchProfileService.get_search_profile_by_id(
        search_profile_id, current_user
    )


@router.get(
    "/{search_profile_id}/overview", response_model=ArticleOverviewResponse
)
async def get_search_profile_overview(search_profile_id: UUID):
    return await SearchProfileService.get_article_overview(search_profile_id)


@router.get(
    "/{search_profile_id}/article/{match_id}",
    response_model=MatchDetailResponse,
)
async def get_match_detail(search_profile_id: UUID, match_id: UUID):
    return await SearchProfileService.get_match_detail(
        search_profile_id, match_id
    )


@router.post("", response_model=SearchProfileDetailResponse)
async def create_search_profile(
    profile_data: SearchProfileCreateRequest,
    current_user: User = Depends(get_authenticated_user),
):
    return await SearchProfileService.create_search_profile(
        profile_data, current_user
    )


@router.put("/{search_profile_id}", response_model=SearchProfileDetailResponse)
async def update_search_profile(
    search_profile_id: UUID,
    update_data: SearchProfileUpdateRequest,
    current_user: User = Depends(get_authenticated_user),
):
    updated = await SearchProfileService.update_search_profile(
        search_profile_id, update_data, current_user
    )
    if updated is None:
        raise HTTPException(
            status_code=404, detail="Search profile not found or not editable"
        )
    return updated


@router.put("/{search_profile_id}/article/{match_id}")
async def update_match_feedback(
    search_profile_id: UUID,
    match_id: UUID,
    feedback: MatchFeedbackRequest,
) -> bool:
    updated_match = await SearchProfileService.update_match_feedback(
        search_profile_id, match_id, feedback
    )
    return updated_match
