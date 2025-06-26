from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.models import User
from app.models.organization import OrganizationRead
from app.schemas.organization_schemas import OrganizationCreate
from app.services.organization_service import OrganizationService

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    dependencies=[Depends(get_authenticated_user)],
)

logger = get_logger(__name__)


@router.post("/organizations/", response_model=OrganizationRead)
async def create_organization(
    org_in: OrganizationCreate,
    current_user: User = Depends(get_authenticated_user),
):
    return await OrganizationService.create_with_users(org_in, current_user)
