import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserEntity(BaseModel):
    id: uuid.UUID
    clerk_id: str
    email: EmailStr
    first_name: str
    last_name: str
    is_superuser: bool
    language: str = "en"
    organization_id: Optional[uuid.UUID] = None
    organization_name: Optional[str] = None
