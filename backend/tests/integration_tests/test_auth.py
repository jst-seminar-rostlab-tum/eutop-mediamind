from unittest.mock import patch

import pytest

from app.core.dependencies import get_current_user


@pytest.mark.anyio
def test_signup_success(client):
    with patch(
        "app.api.v1.endpoints.auth._make_supabase_request",
        return_value={"id": "u"},
    ):
        res = client.post(
            "/api/v1/auth/signup",
            json={"email": "a@b.com", "password": "12345678"},
        )
        assert res.status_code == 200


@pytest.mark.anyio
def test_signup_failure(client):
    with patch(
        "app.api.v1.endpoints.auth._make_supabase_request",
        side_effect=Exception("fail"),
    ):
        res = client.post(
            "/api/v1/auth/signup", json={"email": "a@b.com", "password": "x"}
        )
        assert res.status_code >= 400


@pytest.mark.anyio
def test_login_success(client):
    with patch(
        "app.api.v1.endpoints.auth._make_supabase_request",
        return_value={"access_token": "abc"},
    ):
        res = client.post(
            "/api/v1/auth/login", data={"username": "a", "password": "b"}
        )
        assert res.status_code == 200


@pytest.mark.anyio
def test_login_failure(client):
    with patch(
        "app.api.v1.endpoints.auth._make_supabase_request",
        side_effect=Exception("bad login"),
    ):
        res = client.post(
            "/api/v1/auth/login", data={"username": "a", "password": "b"}
        )
        assert res.status_code >= 400


@pytest.mark.anyio
def test_sso_signin(client):
    res = client.get("/api/v1/auth/signin?provider=google")
    assert res.status_code == 200
    assert "url" in res.json()


@pytest.mark.anyio
def test_sso_callback(client):
    res = client.get("/api/v1/auth/callback")
    assert res.status_code == 200
    assert "message" in res.json()


@pytest.mark.anyio
def test_auth_status_authenticated(client):
    async def mock_user():
        return {"sub": "u", "email": "a@b.com", "role": "authenticated"}

    client.app.dependency_overrides[get_current_user] = mock_user
    res = client.get("/api/v1/auth/status")
    assert res.status_code == 200
    assert res.json()["authenticated"] is True
    client.app.dependency_overrides.clear()


@pytest.mark.anyio
def test_auth_status_unauthenticated(client):
    async def mock_none():
        return None

    client.app.dependency_overrides[get_current_user] = mock_none
    res = client.get("/api/v1/auth/status")
    assert res.status_code == 200
    assert res.json()["authenticated"] is False
    client.app.dependency_overrides.clear()


@pytest.mark.anyio
def test_logout_success(client):
    async def mock_user():
        return {"access_token": "abc"}

    client.app.dependency_overrides[get_current_user] = mock_user
    with patch(
        "app.api.v1.endpoints.auth._make_supabase_request", return_value={}
    ):
        res = client.post("/api/v1/auth/logout")
        assert res.status_code == 200
    client.app.dependency_overrides.clear()


@pytest.mark.anyio
def test_logout_failure(client):
    async def mock_user():
        return {"access_token": "abc"}

    client.app.dependency_overrides[get_current_user] = mock_user
    with patch(
        "app.api.v1.endpoints.auth._make_supabase_request",
        side_effect=Exception("fail"),
    ):
        res = client.post("/api/v1/auth/logout")
        assert res.status_code >= 400
    client.app.dependency_overrides.clear()
