from uuid import UUID

from pydantic import BaseModel


class TopicCreateRequest(BaseModel):
    name: str


class TopicResponse(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True
