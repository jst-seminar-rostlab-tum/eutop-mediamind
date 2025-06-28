import uuid
from typing import List

from pydantic import BaseModel, EmailStr

from app.schemas.user_schema import UserEntity


# Shared properties
class OrganizationBase(BaseModel):
    name: str
    email: EmailStr


# Properties to receive on creation
class OrganizationCreateOrUpdate(OrganizationBase):
    user_ids: List[uuid.UUID]


# Properties to return
class OrganizationResponse(OrganizationBase):
    id: int
    user_ids: List[UserEntity]


# Properties to return
class OrganizationsResponse(OrganizationBase):
    organizations = List[OrganizationResponse]
