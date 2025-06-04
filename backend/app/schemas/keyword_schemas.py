from pydantic import BaseModel
from uuid import UUID

class KeywordCreateRequest(BaseModel):
    value: str

class KeywordResponse(BaseModel):
    id: UUID
    value: str

    class Config:
        orm_mode = True
