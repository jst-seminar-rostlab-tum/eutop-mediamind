import uuid
from typing import List

from pydantic import BaseModel, EmailStr

from app.models import User


# Shared properties
class OrganizationBase(BaseModel):
    name: str
    email: EmailStr


# Properties to receive on creation
class OrganizationCreateOrUpdate(OrganizationBase):
    user_ids: List[uuid.UUID]


# Properties to return
class OrganizationResponse(OrganizationBase):
    id: uuid.UUID
    users: List[User] = []


# Properties to return
class OrganizationsResponse(BaseModel):
    organizations: List[OrganizationResponse]
