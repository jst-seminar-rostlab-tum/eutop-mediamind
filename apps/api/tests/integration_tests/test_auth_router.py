from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def async_return(result):
    async def _coroutine(*args, **kwargs):
        return result

    return _coroutine


def test_signup_missing_required_fields():
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email_address": "apitest1@example.com",
            "password": "test123",
        },
    )
    assert response.status_code == 404
