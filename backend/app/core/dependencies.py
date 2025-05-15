import httpx
from fastapi import Depends
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

from app.core.config import configs
from app.core.exceptions import AuthError

bearer_scheme = HTTPBearer()
SUPABASE_URL = configs.SUPABASE_URL
SUPABASE_KEY = configs.SUPABASE_KEY
SUPABASE_JWT_SECRET = configs.SUPABASE_JWT_SECRET


async def get_current_user(credentials=Depends(bearer_scheme)):
    """Get current authenticated user"""
    token = credentials.credentials

    # verify JWT token
    if SUPABASE_JWT_SECRET:
        try:
            payload = jwt.decode(
                token, SUPABASE_JWT_SECRET, algorithms=["HS256"]
            )
            payload["access_token"] = token
            return payload
        except JWTError:
            print(
                "[INFO] Local JWT verification failed. "
                "Falling back to Supabase API."
            )

    # call Supabase API to verify token
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise AuthError(detail="Supabase configuration missing")

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user", headers=headers
        )

        if response.status_code >= 400:
            raise AuthError(detail="Invalid token or token expired")

        user_data = response.json()
        return {
            "sub": user_data.get("id"),
            "email": user_data.get("email"),
            "role": "authenticated",
            "access_token": token,
        }
