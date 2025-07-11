from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TopicCreateOrUpdateRequest(BaseModel):
    name: str
    keywords: list[str]


class TopicResponse(BaseModel):
    id: UUID
    name: str
    keywords: list[str]

    model_config = ConfigDict(from_attributes=True)
