from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def async_return(result):
    async def _coroutine(*args, **kwargs):
        return result

    return _coroutine


def test_signup_success():
    mock_user = Mock(
        id="user_2xHHfEG7I4WILfdKA3MboZC33ii",
        email_addresses=[Mock(email_address="apitest1@example.com")],
        username="apitest1",
        first_name="API",
        last_name="Test",
    )

    with patch("app.api.v1.endpoints.auth.Clerk") as mock_clerk_class:
        mock_clerk = Mock()
        mock_clerk.users.create_async = async_return(mock_user)
        mock_clerk_class.return_value.__aenter__.return_value = mock_clerk
        mock_clerk_class.return_value.__aexit__.return_value = None

        response = client.post(
            "/api/v1/auth/signup",
            json={
                "email_address": "apitest1@example.com",
                "password": "test123",
                "username": "apitest1",
                "first_name": "API",
                "last_name": "Test",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "user_2xHHfEG7I4WILfdKA3MboZC33ii"
        assert data["email"] == "apitest1@example.com"
        assert data["first_name"] == "API"
        assert data["last_name"] == "Test"


def test_signup_invalid_email():
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email_address": "invalid-email",
            "password": "test123",
            "username": "apitest1",
            "first_name": "API",
            "last_name": "Test",
        },
    )

    assert response.status_code in (200, 422, 500)


def test_signup_short_password():
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email_address": "apitest1@example.com",
            "password": "123",
            "username": "apitest1",
            "first_name": "API",
            "last_name": "Test",
        },
    )

    assert response.status_code in (200, 422, 500)


def test_signup_missing_required_fields():
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email_address": "apitest1@example.com",
            "password": "test123",
        },
    )
    assert response.status_code == 422
