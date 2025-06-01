from unittest.mock import Mock, patch, AsyncMock

import httpx
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.auth import get_authenticated_user


FAKE_JWT = "valid.jwt.token"
FAKE_USER_ID = "00000000-0000-0000-0000-000000000000"

@pytest.mark.asyncio
@patch("app.core.auth.verify_token")
@patch("app.core.auth.Clerk")
async def test_get_authenticated_user_success(mock_clerk_class, mock_verify_token):
    # Step 1: Mock verify_token return
    mock_verify_token.return_value = {
        "sub": FAKE_USER_ID,
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
    }

    # Step 2: Mock Clerk().users.get_async(...)
    mock_user_obj = Mock()
    mock_user_obj.id = FAKE_USER_ID
    mock_user_obj.first_name = "Test"
    mock_user_obj.last_name = "User"
    mock_user_obj.email_addresses = [Mock(email_address="test@example.com")]

    mock_clerk_instance = AsyncMock()
    mock_clerk_instance.__aenter__.return_value = mock_clerk_instance
    mock_clerk_instance.users.get_async.return_value = mock_user_obj
    mock_clerk_class.return_value = mock_clerk_instance

    # Call function
    credentials = Mock(spec=HTTPAuthorizationCredentials)
    credentials.credentials = FAKE_JWT

    user = await get_authenticated_user(credentials)

    assert user["id"] == FAKE_USER_ID
    assert user["email"] == "test@example.com"
    assert user["first_name"] == "Test"
    assert user["last_name"] == "User"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {}
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "401 error", request=Mock(), response=mock_response
        )
        mock_get.return_value = mock_response
        credentials = Mock(credentials="invalid.token")
        with pytest.raises(HTTPException) as exc_info:
            await get_authenticated_user(credentials)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid authentication token"
