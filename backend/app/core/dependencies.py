import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import configs

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        # Get user data using Clerk Secret Key
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.clerk.dev/v1/users",
                headers={
                    "Authorization": f"Bearer {configs.CLERK_SECRET_KEY}",
                    "Content-Type": "application/json",
                },
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                )

            users = response.json()
            # For now, return the first user as a test
            if users and len(users) > 0:
                return users[0]
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No users found",
                )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
