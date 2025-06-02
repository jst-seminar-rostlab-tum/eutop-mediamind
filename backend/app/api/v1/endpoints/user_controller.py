from fastapi import APIRouter, Depends

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.models.user import UserCreate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

logger = get_logger(__name__)


@router.get("")
async def list_users(_: Depends = Depends(get_authenticated_user)):
    return await UserService.list_users()


@router.get("/me")
async def get_current_user_info(current_user=Depends(get_authenticated_user)):
    return UserService.get_current_user_info(current_user)


@router.post("/sync", response_model=dict)
async def sync_user_with_clerk(user_data=Depends(get_authenticated_user)):
    user_create = UserCreate(
        clerk_id=user_data["id"],
        email=user_data["email"],
        first_name=user_data.get("first_name"),
        last_name=user_data.get("first_name"),
        is_superuser=False,
        organization_id=None,
    )
    user = await UserService.create_user_if_not_exists(user_create)
    return {"id": str(user.id)}
