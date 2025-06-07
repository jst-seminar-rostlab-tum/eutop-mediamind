from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_authenticated_user
from app.schemas.topic_schemas import TopicCreateOrUpdateRequest, TopicResponse
from app.services.topics_service import TopicsService

router = APIRouter(
    prefix="/search-profiles/{search_profile_id}/topics",
    tags=["topics"],
    dependencies=[Depends(get_authenticated_user)],
)


@router.get("", response_model=list[TopicResponse])
async def get_topics(
    search_profile_id: UUID, current_user=Depends(get_authenticated_user)
):
    raise HTTPException(status_code=404, detail="Not implemented")
    return await TopicsService.get_topics(search_profile_id, current_user)


@router.post("", response_model=TopicResponse)
async def add_topic(
    search_profile_id: UUID,
    request: TopicCreateOrUpdateRequest,
    current_user=Depends(get_authenticated_user),
):
    raise HTTPException(status_code=404, detail="Not implemented")
    return await TopicsService.add_topic(
        search_profile_id, request, current_user
    )


@router.delete("/{topic_id}")
async def delete_topic(
    search_profile_id: UUID,
    topic_id: UUID,
    current_user=Depends(get_authenticated_user),
):
    raise HTTPException(status_code=404, detail="Not implemented")
    return await TopicsService.delete_topic(
        search_profile_id, topic_id, current_user
    )
