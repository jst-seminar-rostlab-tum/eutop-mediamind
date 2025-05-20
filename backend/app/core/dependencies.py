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
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        )
