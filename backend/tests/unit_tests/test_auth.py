from unittest.mock import Mock, patch

import httpx
import pytest
from fastapi import HTTPException

from app.core.auth import get_authenticated_user

FAKE_JWT = "valid.jwt.token"
FAKE_USER_ID = "00000000-0000-0000-0000-000000000000"


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
