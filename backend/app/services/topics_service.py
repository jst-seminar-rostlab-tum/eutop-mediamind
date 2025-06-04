from uuid import UUID

from fastapi import HTTPException, status

from app.models.user import User
from app.repositories.topics_repository import TopicsRepository
from app.schemas.topic_schemas import TopicCreateRequest


class TopicsService:
    @staticmethod
    async def get_topics(profile_id: UUID, user: User):
        return await TopicsRepository.get_topics_by_profile(profile_id, user)

    @staticmethod
    async def add_topic(
        profile_id: UUID, request: TopicCreateRequest, user: User
    ):
        return await TopicsRepository.add_topic(profile_id, request, user)

    @staticmethod
    async def delete_topic(profile_id: UUID, topic_id: UUID, user: User):
        success = await TopicsRepository.delete_topic(
            profile_id, topic_id, user
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found or unauthorized.",
            )
        return {"message": "Topic deleted"}
