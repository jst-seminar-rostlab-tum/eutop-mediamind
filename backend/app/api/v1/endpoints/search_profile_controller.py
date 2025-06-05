from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_authenticated_user
from app.models import User
from app.models.search_profile import (
    SearchProfileCreate,
    SearchProfileRead,
    SearchProfileUpdate,
)
from app.schemas.articles_schemas import (
    ArticleOverviewResponse,
    MatchDetailResponse,
)
from app.schemas.match_schemas import MatchFeedbackRequest
from app.schemas.search_profile_schemas import SearchProfileDetailResponse
from app.services.search_profiles_service import SearchProfiles

router = APIRouter(
    prefix="/search-profiles",
    tags=["search-profiles"],
    dependencies=[Depends(get_authenticated_user)],
)


@router.post("/create", response_model=SearchProfileRead, status_code=201)
async def create_search_profile(
    profile_data: SearchProfileCreate,
    current_user: User = Depends(get_authenticated_user),
):
    return await SearchProfiles.create_search_profile(
        profile_data, current_user
    )


@router.get("/{search_profile_id}", response_model=SearchProfileDetailResponse)
async def get_search_profile(
    search_profile_id: UUID, current_user=Depends(get_authenticated_user)
):
    return await SearchProfiles.get_search_profile_by_id(
        search_profile_id, current_user
    )


@router.get("", response_model=list[SearchProfileDetailResponse])
async def get_available_search_profiles(
    current_user=Depends(get_authenticated_user),
):
    return await SearchProfiles.get_available_search_profiles(current_user)


@router.put("/{search_profile_id}", response_model=SearchProfileRead)
async def update_search_profile(
    search_profile_id: UUID,
    update_data: SearchProfileUpdate,
    current_user: User = Depends(get_authenticated_user),
):
    updated = await SearchProfiles.update_search_profile(
        search_profile_id, update_data, current_user
    )
    if updated is None:
        raise HTTPException(
            status_code=404, detail="Search profile not found or not editable"
        )
    return updated


@router.get(
    "/{search_profile_id}/overview", response_model=ArticleOverviewResponse
)
async def get_search_profile_overview(search_profile_id: UUID):
    return await SearchProfiles.get_article_overview(search_profile_id)


@router.get(
    "/{search_profile_id}/article/{match_id}",
    response_model=MatchDetailResponse,
)
async def get_match_detail(search_profile_id: UUID, match_id: UUID):
    return await SearchProfiles.get_match_detail(search_profile_id, match_id)


@router.put("/{search_profile_id}/article/{match_id}")
async def update_match_feedback(
    search_profile_id: UUID,
    match_id: UUID,
    feedback: MatchFeedbackRequest,
) -> MatchDetailResponse:
    updated_match = await SearchProfiles.update_match_feedback(
        search_profile_id, match_id, feedback
    )
    return updated_match
