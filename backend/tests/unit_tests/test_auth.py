from unittest.mock import Mock, patch, AsyncMock

import httpx
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from starlette import status

from app.core.auth import get_authenticated_user
from app.core.config import configs

FAKE_JWT = "valid.jwt.token"
FAKE_USER_ID = "00000000-0000-0000-0000-000000000000"

@pytest.mark.asyncio
async def test_get_current_user_invalid_token(monkeypatch):
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.json.return_value = {}
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "401 error", request=Mock(), response=mock_response
    )

    async def fake_get(*args, **kwargs):
        return mock_response

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)

    request = Mock()
    request.cookies = {configs.CLERK_COOKIE_NAME: "invalid.token"}

    with pytest.raises(HTTPException) as exc_info:
        await get_authenticated_user(request)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid authentication token"
