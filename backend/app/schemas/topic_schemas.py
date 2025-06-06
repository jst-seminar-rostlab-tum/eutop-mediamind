from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TopicCreateRequest(BaseModel):
    name: str
    keywords: list[str]


class TopicResponse(BaseModel):
    id: UUID
    name: str
    keywords: list[str]

    model_config = ConfigDict(from_attributes=True)


class TopicUpdateRequest(BaseModel):
    name: str
    keywords: list[str]
