import uuid
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.auth import get_authenticated_user
from app.main import app

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
    }




def test_list_users_unauthorized():
    response = client.get("/api/v1/users")
    assert response.status_code == 403


def test_list_users_success(mock_user_data):
    mock_token = "valid.jwt.token"
    # override dependency
    app.dependency_overrides[get_authenticated_user] = lambda: mock_user_data

    mock_users = [
        Mock(
            id="user_2xHHfEG7I4WILfdKA3MboZC33ii",
            email_addresses=[Mock(email_address="apitest1@example.com")],
            first_name="API",
            last_name="Test",
        ),
        Mock(
            id="user_2xHDRsRd8HqCsRmXVxRi0WRuwuk",
            email_addresses=[Mock(email_address="test2@example.com")],
            first_name="Test2",
            last_name="User2",
        ),
    ]

    with patch("app.services.user_service.Clerk") as mock_clerk_class:
        mock_clerk = Mock()
        mock_clerk.users.list_async = async_return(mock_users)
        mock_clerk_class.return_value.__aenter__.return_value = mock_clerk
        mock_clerk_class.return_value.__aexit__.return_value = None

        response = client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {mock_token}"},
        )

        if response.status_code != 200:
            print(f"Error response: {response.json()}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["users"]) == 2
        assert data["users"][0]["email"] == "apitest1@example.com"
        assert data["users"][1]["email"] == "test2@example.com"

    # clean up dependency override
    app.dependency_overrides = {}
