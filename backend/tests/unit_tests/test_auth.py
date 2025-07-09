import pytest
from fastapi import HTTPException
from starlette import status

from app.core.auth import get_authenticated_user
from app.core.config import configs


class DummyRequest:
    def __init__(self, cookies: dict):
        self.cookies = cookies


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(monkeypatch):
    def fake_verify(token, options):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    monkeypatch.setattr(
        "app.core.auth.verify_token",
        fake_verify,
    )

    request = DummyRequest({configs.CLERK_COOKIE_NAME: "invalid.token"})

    with pytest.raises(HTTPException) as exc_info:
        await get_authenticated_user(request)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid authentication token"
