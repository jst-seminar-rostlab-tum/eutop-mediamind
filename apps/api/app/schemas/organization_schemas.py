import uuid
from typing import List

from pydantic import BaseModel, EmailStr

from app.models import User
from app.models.user import UserRole
from app.schemas.subscription_schemas import SubscriptionSummary


# Shared properties
class OrganizationBase(BaseModel):
    name: str
    email: EmailStr or None
    pdf_as_link: bool


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
    subscriptions: List[SubscriptionSummary] = []
