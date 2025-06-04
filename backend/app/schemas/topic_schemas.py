from pydantic import BaseModel
from uuid import UUID

class TopicCreateRequest(BaseModel):
    name: str

class TopicResponse(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True
