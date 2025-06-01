from clerk_backend_api import Clerk
from clerk_backend_api.jwks_helpers import VerifyTokenOptions, verify_token
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import configs
from app.core.logger import get_logger

security = HTTPBearer()
logger = get_logger(__name__)


async def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials

        # Step 1: Verify token
        user_claim = verify_token(
            token,
            VerifyTokenOptions(
                secret_key=configs.CLERK_SECRET_KEY,
            ),
        )

        user_id = user_claim["sub"]

        if not user_id:
            raise HTTPException(
                status_code=401, detail="Missing user ID in token"
            )

        # Step 2: Use Clerk SDK to fetch the user
        async with Clerk(bearer_auth=configs.CLERK_SECRET_KEY) as clerk:
            user = await clerk.users.get_async(user_id=user_id)

        return {
            "id": user.id,
            "email": (
                user.email_addresses[0].email_address
                if user.email_addresses
                else None
            ),
            "first_name": user.first_name,
            "last_name": user.last_name,
        }

    except Exception as e:
        logger.warning(f"Auth failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
