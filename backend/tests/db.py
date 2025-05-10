from src.db import get_supabase_client
import pytest

# EXAMPLE TESTS FOR COVERAGE PIPELINE


def test_get_supabase_client(monkeypatch):
    mock_url = "https://mockurl.supabase.co"
    mock_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    monkeypatch.setenv("SUPABASE_URL", mock_url)
    monkeypatch.setenv("SUPABASE_KEY", mock_key)

    client = get_supabase_client()
    assert client is not None


def test_get_supabase_client_no_env(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)

    with pytest.raises(Exception) as excinfo:
        get_supabase_client()
    assert "Supabase credentials are not set" in str(excinfo.value)


def test_get_supabase_client_invalid_credentials(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "invalid-url-format")
    monkeypatch.setenv("SUPABASE_KEY", "invalid-key-format")

    with pytest.raises(Exception) as excinfo:
        get_supabase_client()
    assert "Failed to initialize Supabase client" in str(excinfo.value)
    assert "Invalid URL" in str(excinfo.value)
