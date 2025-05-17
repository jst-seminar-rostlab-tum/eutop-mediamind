import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from app.main import app

client = TestClient(app)

def test_get_current_user_info_unauthorized():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403  # FastAPI's HTTPBearer returns 403 for missing token

def test_get_current_user_info_success():
    mock_user_data = [{
        "id": "user_123",
        "email_addresses": [{"email_address": "test@example.com"}],
        "first_name": "Test",
        "last_name": "User"
    }]
    mock_token = "valid.jwt.token"
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_user_data
        mock_get.return_value = mock_response
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {mock_token}"}
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

def test_list_users_success():
    mock_user_data = [{
        "id": "user_123",
        "email_addresses": [{"email_address": "test@example.com"}],
        "first_name": "Test",
        "last_name": "User"
    }]
    mock_token = "valid.jwt.token"
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_user_data
        mock_get.return_value = mock_response
        response = client.get(
            "/api/v1/auth/users",
            headers={"Authorization": f"Bearer {mock_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["users"]) == 1
        user = data["users"][0]
        assert user["id"] == "user_123"
        assert user["email"] == "test@example.com"
        assert user["first_name"] == "Test"
        assert user["last_name"] == "User"
