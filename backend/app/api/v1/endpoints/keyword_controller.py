from uuid import UUID
from fastapi import APIRouter, Depends

from app.core.auth import get_authenticated_user
from app.schemas.keyword_schemas import KeywordCreateRequest, KeywordResponse
from app.services.keywords_service import KeywordsService

router = APIRouter(
    prefix="/topics/{topic_id}/keywords",
    tags=["keywords"],
    dependencies=[Depends(get_authenticated_user)],
)

@router.get("", response_model=list[KeywordResponse])
async def get_keywords(topic_id: UUID, current_user=Depends(get_authenticated_user)):
    return await KeywordsService.get_keywords(topic_id, current_user)


@router.post("", response_model=KeywordResponse)
async def add_keyword(
    topic_id: UUID,
    request: KeywordCreateRequest,
    current_user=Depends(get_authenticated_user)
):
    return await KeywordsService.add_keyword(topic_id, request, current_user)


@router.delete("/{keyword_id}")
async def delete_keyword(
    topic_id: UUID,
    keyword_id: UUID,
    current_user=Depends(get_authenticated_user)
):
    return await KeywordsService.delete_keyword(topic_id, keyword_id, current_user)
