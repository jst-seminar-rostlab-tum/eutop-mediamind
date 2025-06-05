from uuid import UUID

from fastapi import HTTPException
from starlette import status

from app.models import User
from app.repositories.topics_repository import TopicsRepository
from app.schemas.topic_schemas import TopicCreateRequest


class TopicsService:
    @staticmethod
    async def get_topics(search_profile_id: UUID, user: User):
        topics = await TopicsRepository.get_topics_by_search_profile(
            search_profile_id, user
        )
        if not topics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No topics found or access denied to search profile.",
            )
        return topics

    @staticmethod
    async def add_topic(
        search_profile_id: UUID, request: TopicCreateRequest, user: User
    ):
        topic = await TopicsRepository.add_topic(
            search_profile_id, request, user
        )
        if topic is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to add topic to this search profile.",
            )
        return topic

    @staticmethod
    async def delete_topic(
        search_profile_id: UUID, topic_id: UUID, user: User
    ):
        success = await TopicsRepository.delete_topic(
            search_profile_id, topic_id, user
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found or unauthorized.",
            )
        return {"message": "Topic deleted"}
