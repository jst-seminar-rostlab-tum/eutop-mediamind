from uuid import UUID

from pydantic import BaseModel


class KeywordCreateRequest(BaseModel):
    value: str


class KeywordResponse(BaseModel):
    id: UUID
    value: str
