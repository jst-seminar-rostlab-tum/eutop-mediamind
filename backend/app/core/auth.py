from clerk_backend_api import Clerk
from clerk_backend_api.jwks_helpers import VerifyTokenOptions, verify_token
from fastapi import Request, HTTPException, status

from app.core.config import configs
from app.core.logger import get_logger
from app.models import User
from app.repositories.user_repository import (
    create_user,
    get_user_by_clerk_id,
    update_user,
)

logger = get_logger(__name__)


async def get_authenticated_user(request: Request) -> User:
    try:
        if configs.DISABLE_AUTH:
            user_clerk_id = "user_2xd0q4SUzIlYIZZnUZ2UmNmHz8n"
        else:
            token = request.cookies.get("__session")
            if not token:
                raise HTTPException(
                    status_code=401,
                    detail="Missing authentication token in cookies",
                )

            # Step 1: Verify token
            user_claim = verify_token(
                token,
                VerifyTokenOptions(
                    secret_key=configs.CLERK_SECRET_KEY,
                ),
            )

            user_clerk_id = user_claim["sub"]

            if not user_clerk_id:
                raise HTTPException(
                    status_code=401, detail="Missing user ID in token"
                )

        # User from local DB
        user = await get_user_by_clerk_id(user_clerk_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    except Exception as e:
        logger.warning(f"Auth failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )


async def get_sync_user(request: Request) -> User:
    try:
        if configs.DISABLE_AUTH:
            user_clerk_id = "user_2xd0q4SUzIlYIZZnUZ2UmNmHz8n"
        else:
            token = request.cookies.get("__session")
            if not token:
                raise HTTPException(
                    status_code=401,
                    detail="Missing authentication token in cookies",
                )

            # Step 1: Verify the token and extract the Clerk user ID (sub)
            user_claim = verify_token(
                token,
                VerifyTokenOptions(secret_key=configs.CLERK_SECRET_KEY),
            )

            user_clerk_id = user_claim["sub"]
            if not user_clerk_id:
                raise HTTPException(
                    status_code=401, detail="Missing user ID in token"
                )

        # Step 2: Fetch the user from Clerk
        async with Clerk(bearer_auth=configs.CLERK_SECRET_KEY) as clerk:
            clerk_user = await clerk.users.get_async(user_id=user_clerk_id)
            clerk_user_data = clerk_user.model_dump()

            # Extract email from nested Clerk structure
            clerk_email = (
                clerk_user_data.get("email_addresses", [{}])[0].get(
                    "email_address"
                )
                if clerk_user_data.get("email_addresses")
                else None
            )

            # Step 3: Try to fetch user from local database
            user = await get_user_by_clerk_id(user_clerk_id)

            # Step 4: If user does not exist, create it
            if not user:
                user = User(
                    clerk_id=user_clerk_id,
                    email=clerk_email,
                    first_name=clerk_user_data.get("first_name"),
                    last_name=clerk_user_data.get("last_name"),
                )
                user = await create_user(user)

            # Step 5: Synchronize selected fields if needed
            updated = False

            if (
                clerk_user_data.get("first_name")
                and user.first_name != clerk_user_data["first_name"]
            ):
                user.first_name = clerk_user_data["first_name"]
                updated = True

            if (
                clerk_user_data.get("last_name")
                and user.last_name != clerk_user_data["last_name"]
            ):
                user.last_name = clerk_user_data["last_name"]
                updated = True

            if clerk_email and user.email != clerk_email:
                user.email = clerk_email
                updated = True

            if updated:
                user = await update_user(user)

        return user

    except Exception as e:
        logger.warning(f"Auth failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
