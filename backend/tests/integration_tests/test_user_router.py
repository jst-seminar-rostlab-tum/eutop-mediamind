from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.v1.endpoints import auth as auth_module
from app.main import app

client = TestClient(app)


def test_get_current_user_info_unauthorized():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403


@pytest.fixture
def mock_user_data():
    return {
        "id": "user_123",
        "email_addresses": [{"email_address": "test@example.com"}],
        "first_name": "Test",
        "last_name": "User",
    }


def test_get_current_user_info_success(mock_user_data):
    mock_token = "valid.jwt.token"
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_user_data
        mock_get.return_value = mock_response
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {mock_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "user_123"
        assert data["email"] == "test@example.com"
        assert data["first_name"] == "Test"
        assert data["last_name"] == "User"


def test_list_users_unauthorized():
    response = client.get("/api/v1/auth/users")
    assert response.status_code == 403


def test_list_users_success(mock_user_data):
    mock_token = "valid.jwt.token"
    # override dependency
    app.dependency_overrides[auth_module.get_current_user] = (
        lambda: mock_user_data
    )
    with patch("app.api.v1.endpoints.auth.clerk.users.list") as mock_list:
        # mock multiple users data
        mock_list.return_value = [
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
        response = client.get(
            "/api/v1/auth/users",
            headers={"Authorization": f"Bearer {mock_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["users"]) == 2
        assert data["users"][0]["email"] == "apitest1@example.com"
        assert data["users"][1]["email"] == "test2@example.com"
    # clean up dependency override
    app.dependency_overrides = {}
