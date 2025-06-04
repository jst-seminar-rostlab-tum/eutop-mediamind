from uuid import UUID
from fastapi import HTTPException, status

from app.repositories.keyword_repository import KeywordsRepository
from app.models.user import User
from app.schemas.keyword_schemas import KeywordCreateRequest

class KeywordsService:
    @staticmethod
    async def get_keywords(topic_id: UUID, user: User):
        return await KeywordsRepository.get_keywords_by_topic(topic_id, user)

    @staticmethod
    async def add_keyword(topic_id: UUID, request: KeywordCreateRequest, user: User):
        return await KeywordsRepository.add_keyword(topic_id, request, user)

    @staticmethod
    async def delete_keyword(topic_id: UUID, keyword_id: UUID, user: User):
        success = await KeywordsRepository.delete_keyword(topic_id, keyword_id, user)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Keyword not found or unauthorized.")
        return {"message": "Keyword deleted"}
