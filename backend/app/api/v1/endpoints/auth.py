from typing import Dict, Optional

import httpx
from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from app.core.config import configs
from app.core.dependencies import get_current_user
from app.core.exceptions import AuthError


# define request model
class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    redirect_to: Optional[str] = None


router = APIRouter(prefix="/auth", tags=["authentication"])

# Supabase config
SUPABASE_URL = configs.SUPABASE_URL
SUPABASE_KEY = configs.SUPABASE_KEY
AUTH_BASE_URL = f"{SUPABASE_URL}/auth/v1"
SUPABASE_HEADERS = {"apikey": SUPABASE_KEY, "Content-Type": "application/json"}


async def _make_supabase_request(
    method: str, url: str, expect_json: bool = True, **kwargs
) -> Dict:
    """Make a request to Supabase API with error handling"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise AuthError(detail="Supabase configuration missing")

    try:
        async with httpx.AsyncClient() as client:
            response = await getattr(client, method)(url, **kwargs)
            response.raise_for_status()
            return response.json() if expect_json else {}
    except httpx.HTTPStatusError as e:
        error_data = (
            e.response.json() if e.response.content else {"msg": str(e)}
        )
        error_msg = error_data.get("msg", "Unknown error")
        raise AuthError(detail=f"Request failed: {error_msg}")
    except httpx.RequestError as e:
        raise AuthError(detail=f"Request failed: {str(e)}")


@router.post("/signup")
async def signup(data: SignupRequest):
    """register a new user"""
    try:
        payload = {
            "email": data.email,
            "password": data.password,
            "data": {},
            "redirect_to": data.redirect_to or configs.REDIRECT_URL,
        }
        return await _make_supabase_request(
            "post",
            f"{AUTH_BASE_URL}/signup",
            json=payload,
            headers=SUPABASE_HEADERS,
        )
    except AuthError as e:
        raise e
    except Exception as e:
        raise AuthError(detail=str(e))


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """user login"""
    try:
        payload = {"email": form_data.username, "password": form_data.password}
        return await _make_supabase_request(
            "post",
            f"{AUTH_BASE_URL}/token?grant_type=password",
            json=payload,
            headers=SUPABASE_HEADERS,
        )
    except AuthError as e:
        raise e
    except Exception as e:
        raise AuthError(detail=str(e))


@router.get("/signin")
def sso_signin(provider: str):
    redirect = configs.REDIRECT_URL
    url = (
        f"{AUTH_BASE_URL}/authorize?"
        f"provider={provider}&"
        f"redirect_to={redirect}"
    )
    return {"url": url}


@router.get("/callback")
async def sso_callback(request: Request):
    return {
        "message": (
            "SSO callback handled here "
            "(use frontend to parse token from hash)."
        )
    }


@router.post("/logout")
async def logout(
    current_user: dict = Depends(get_current_user), response: Response = None
):
    """User logout"""
    try:
        token = current_user.get("access_token")
        headers = {**SUPABASE_HEADERS, "Authorization": f"Bearer {token}"}

        await _make_supabase_request(
            "post",
            f"{AUTH_BASE_URL}/logout",
            headers=headers,
            expect_json=False,  # Supabase logout endpoint returns empty
        )

        if response:
            response.delete_cookie("supabase-auth")
        return {"success": True, "message": "Successfully logged out"}
    except AuthError as e:
        raise e
    except Exception as e:
        raise AuthError(detail=str(e))


@router.get("/status")
async def auth_status(
    current_user: Optional[dict] = Depends(get_current_user),
):
    """check auth status"""
    if current_user:
        return {
            "authenticated": True,
            "user": {
                "id": current_user.get("sub"),
                "email": current_user.get("email"),
                "role": current_user.get("role"),
            },
        }

    return {"authenticated": False}
