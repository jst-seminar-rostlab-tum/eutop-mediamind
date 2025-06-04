import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.core.auth import get_authenticated_user
from app.main import app
from app.models import User

client = TestClient(app)


def async_return(result):
    async def _coroutine(*args, **kwargs):
        return result

    return _coroutine


def test_get_current_user_info_unauthorized():
    response = client.get("/api/v1/users/me")
    assert response.status_code == 403


@pytest.fixture
def mock_user_data():
    return {
        "id": "00000000-0000-0000-0000-000000000000",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "organization_id": None,
        "clerk_id": None,
    }




def test_list_users_unauthorized():
    response = client.get("/api/v1/users")
    assert response.status_code == 403
