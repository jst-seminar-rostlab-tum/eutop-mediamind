from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from app.core.dependencies import get_current_user


@pytest.mark.asyncio
async def test_get_current_user_success():
    mock_user_data = {
        "id": "user_123",
        "email_addresses": [{"email_address": "test@example.com"}],
        "first_name": "Test",
        "last_name": "User",
    }
    mock_token = "valid.jwt.token"
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_user_data
        mock_get.return_value = mock_response
        credentials = Mock(credentials=mock_token)
        user = await get_current_user(credentials)
        assert user["id"] == "user_123"
        assert (
            user["email_addresses"][0]["email_address"] == "test@example.com"
        )
        assert user["first_name"] == "Test"
        assert user["last_name"] == "User"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response
        credentials = Mock(credentials="invalid.token")
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid authentication credentials"
