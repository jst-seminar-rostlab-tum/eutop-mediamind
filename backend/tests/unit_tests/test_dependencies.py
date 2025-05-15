from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from jose import jwt

from app.core.dependencies import get_current_user
from app.core.exceptions import AuthError


@pytest.mark.asyncio
async def test_get_current_user_with_valid_jwt():
    # Arrange
    test_payload = {
        "sub": "user123",
        "email": "test@example.com",
        "role": "user",
    }
    token = jwt.encode(test_payload, "test_secret", algorithm="HS256")
    mock_credentials = AsyncMock()
    mock_credentials.credentials = token

    with patch("app.core.dependencies.SUPABASE_JWT_SECRET", "test_secret"):
        # Act
        result = await get_current_user(mock_credentials)

        # Assert
        assert result["sub"] == test_payload["sub"]
        assert result["email"] == test_payload["email"]
        assert result["role"] == test_payload["role"]


@pytest.mark.asyncio
async def test_get_current_user_with_invalid_jwt():
    # Arrange
    mock_credentials = AsyncMock()
    mock_credentials.credentials = "invalid_token"

    with (
        patch("app.core.dependencies.SUPABASE_JWT_SECRET", "test_secret"),
        patch("app.core.dependencies.SUPABASE_URL", "http://test"),
        patch("app.core.dependencies.SUPABASE_KEY", "test_key"),
        patch("httpx.AsyncClient") as mock_client,
    ):

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            mock_response
        )

        # Act & Assert
        with pytest.raises(AuthError) as exc_info:
            await get_current_user(mock_credentials)
        assert "Invalid token or token expired" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_current_user_with_supabase_api():
    # Arrange
    mock_credentials = AsyncMock()
    mock_credentials.credentials = "valid_token"
    mock_user_data = {
        "id": "user123",
        "email": "test@example.com",
    }

    with (
        patch("app.core.dependencies.SUPABASE_JWT_SECRET", None),
        patch("app.core.dependencies.SUPABASE_URL", "http://test"),
        patch("app.core.dependencies.SUPABASE_KEY", "test_key"),
        patch("httpx.AsyncClient") as mock_client,
    ):

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_user_data
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            mock_response
        )

        # Act
        result = await get_current_user(mock_credentials)

        # Assert
        assert result["sub"] == mock_user_data["id"]
        assert result["email"] == mock_user_data["email"]
        assert result["role"] == "authenticated"
        assert result["access_token"] == "valid_token"


@pytest.mark.asyncio
async def test_get_current_user_with_missing_config():
    # Arrange
    mock_credentials = AsyncMock()
    mock_credentials.credentials = "valid_token"

    with (
        patch("app.core.dependencies.SUPABASE_JWT_SECRET", None),
        patch("app.core.dependencies.SUPABASE_URL", None),
        patch("app.core.dependencies.SUPABASE_KEY", None),
    ):

        # Act & Assert
        with pytest.raises(AuthError) as exc_info:
            await get_current_user(mock_credentials)
        assert "Supabase configuration missing" in str(exc_info.value)
