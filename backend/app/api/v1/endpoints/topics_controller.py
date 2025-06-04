from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.auth import get_authenticated_user
from app.schemas.topic_schemas import TopicCreateRequest, TopicResponse
from app.services.topics_service import TopicsService

router = APIRouter(
    prefix="/search-profiles/{profile_id}/topics",
    tags=["topics"],
    dependencies=[Depends(get_authenticated_user)],
)


@router.get("", response_model=list[TopicResponse])
async def get_topics(
    profile_id: UUID, current_user=Depends(get_authenticated_user)
):
    return await TopicsService.get_topics(profile_id, current_user)


@router.post("", response_model=TopicResponse)
async def add_topic(
    profile_id: UUID,
    request: TopicCreateRequest,
    current_user=Depends(get_authenticated_user),
):
    return await TopicsService.add_topic(profile_id, request, current_user)


@router.delete("/{topic_id}")
async def delete_topic(
    profile_id: UUID,
    topic_id: UUID,
    current_user=Depends(get_authenticated_user),
):
    return await TopicsService.delete_topic(profile_id, topic_id, current_user)