import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def async_return(result):
    async def _coroutine(*args, **kwargs):
        return result

    return _coroutine


def test_get_current_user_info_unauthorized():
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


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
    assert response.status_code == 401
