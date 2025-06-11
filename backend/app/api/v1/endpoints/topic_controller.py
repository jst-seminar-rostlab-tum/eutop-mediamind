from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.models import Topic, User
from app.repositories.topics_repository import TopicsRepository

router = APIRouter(prefix="/topics", tags=["topics"])

logger = get_logger(__name__)


@router.get("")
async def get_topics_by_search_profile(
    search_profile_id: UUID,
    current_user: User = Depends(get_authenticated_user),
):
    """
    Get topics by search profile ID.
    """
    topics = await TopicsRepository.get_topics_by_search_profile(
        search_profile_id, current_user
    )
    return topics


@router.post("")
async def create_topic_by_search_profile(
    search_profile_id: UUID,
    topic_name: str,
    current_user: User = Depends(get_authenticated_user),
) -> Topic:
    """
    Create a topic by search profile ID.
    """

    topic: Topic = await TopicsRepository.create_topic_by_search_profile(
        search_profile_id, topic_name, current_user
    )
    return topic


@router.delete("/{topic_id}")
async def delete_topic(
    topic_id: UUID, current_user: User = Depends(get_authenticated_user)
):
    """
    Delete a topic by ID.
    """
    result = await TopicsRepository.delete_topic_by_id(topic_id, current_user)
    if not result:
        return {
            "message": "Topic not found or you do not have permission to delete it."
        }
    return {"message": "Topic deleted successfully."}
