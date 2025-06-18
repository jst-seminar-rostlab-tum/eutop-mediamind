from clerk_backend_api import Clerk
from clerk_backend_api.jwks_helpers import VerifyTokenOptions, verify_token
from fastapi import HTTPException, Request, status

from app.core.config import configs
from app.core.logger import get_logger
from app.schemas.user_schema import UserEntity
from app.services.user_service import UserService

logger = get_logger(__name__)


def _extract_clerk_id(request: Request, cookie_name: str) -> str:
    """
    Verify session token in cookies and extract Clerk user ID.
    """
    token = request.cookies.get(cookie_name)
    if not token:
        logger.warning("Failed Authentication Process. Cookie missing", request.client)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    claims = verify_token(
        token,
        VerifyTokenOptions(secret_key=configs.CLERK_SECRET_KEY),
    )
    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing user ID in token",
        )

    return user_id


async def get_authenticated_user(request: Request) -> UserEntity:
    """
    Dependency: Retrieve authenticated user from local database
    via Clerk token.
    """
    clerk_id = (
        "user_2xd0q4SUzIlYIZZnUZ2UmNmHz8n"
        if configs.DISABLE_AUTH
        else _extract_clerk_id(request, configs.CLERK_COOKIE_NAME)
    )

    user = await UserService.get_by_clerk_id(clerk_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


async def get_sync_user(request: Request) -> UserEntity:
    """
    Dependency: Synchronize user from Clerk to local DB and
    return a UserEntity.
    """
    clerk_id = (
        "user_2xd0q4SUzIlYIZZnUZ2UmNmHz8n"
        if configs.DISABLE_AUTH
        else _extract_clerk_id(request, configs.CLERK_COOKIE_NAME)
    )

    async with Clerk(bearer_auth=configs.CLERK_SECRET_KEY) as clerk:
        clerk_user = await clerk.users.get_async(user_id=clerk_id)
        data = clerk_user.model_dump()

    email = (
        data.get("email_addresses", [{}])[0].get("email_address")
        if data.get("email_addresses")
        else None
    )

    existing = await UserService.get_by_clerk_id(clerk_id)
    if not existing:
        return await UserService.create_user_from_clerk(clerk_id, email, data)
    return await UserService.sync_user_fields(existing, email, data)
