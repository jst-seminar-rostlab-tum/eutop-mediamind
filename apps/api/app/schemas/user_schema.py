import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.core.languages import Language
from app.models.user import Gender, UserRole


class UserEntity(BaseModel):
    id: uuid.UUID
    clerk_id: str
    email: EmailStr
    first_name: str
    last_name: str
    is_superuser: bool
    language: str = Language.EN.value
    gender: Optional[Gender] = None
    role: UserRole = UserRole.member
    organization_id: Optional[uuid.UUID] = None
    organization_name: Optional[str] = None
    breaking_news: bool = True
