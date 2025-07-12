import uuid
from typing import List

from pydantic import BaseModel, EmailStr

from app.models import User
from app.models.user import UserRole


# Shared properties
class OrganizationBase(BaseModel):
    name: str
    email: EmailStr or None


class CreateRequestUser(BaseModel):
    id: uuid.UUID
    role: UserRole


# Properties to receive on creation
class OrganizationCreateOrUpdate(OrganizationBase):
    users: List[CreateRequestUser]


# Properties to return
class OrganizationResponse(OrganizationBase):
    id: uuid.UUID
    users: List[User] = []
