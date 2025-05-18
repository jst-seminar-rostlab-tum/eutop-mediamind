import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        # Verify session token with Clerk
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.clerk.dev/v1/me",
                headers={
                    "Authorization": f"Bearer {credentials.credentials}",
                    "Content-Type": "application/json",
                },
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                )

            user = response.json()
            return user

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
