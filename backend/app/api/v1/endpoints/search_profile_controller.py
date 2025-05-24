from fastapi import APIRouter, Depends
from uuid import UUID

from app.core.dependencies import get_current_user
from app.schemas.articles_schemas import ArticleOverviewResponse, MatchDetailResponse
from app.schemas.search_profile_schemas import SearchProfileUpdateRequest, SearchProfileDetailResponse
from app.services.search_profiles_service import SearchProfiles

router = APIRouter(prefix="/search-profiles", tags=["users"])


@router.get("", response_model=list[SearchProfileDetailResponse])
async def get_available_search_profiles(current_user=Depends(get_current_user)):
    return await SearchProfiles.get_available_search_profiles(current_user)



@router.get("/{profile_id}", response_model=SearchProfileDetailResponse)
async def get_search_profile(profile_id: UUID, current_user=Depends(get_current_user)):
    return SearchProfiles.get_search_profile(profile_id, current_user)

@router.put("/{profile_id}")
async def update_search_profile(
    profile_id: UUID,
    request: SearchProfileUpdateRequest,
    current_user=Depends(get_current_user)
):
    updated = await SearchProfiles.update_search_profile(profile_id, request, current_user)
    return updated

@router.get("/{profile_id}/overview", response_model=ArticleOverviewResponse)
async def get_profile_overview(profile_id: UUID):
    overview = await SearchProfiles.get_article_overview(profile_id)
    return overview

@router.get("/{profile_id}/article/{match_id}", response_model=MatchDetailResponse)
async def get_match_detail(profile_id: UUID, match_id: UUID):
    detail = await SearchProfiles.get_match_detail(profile_id, match_id)
    return detail