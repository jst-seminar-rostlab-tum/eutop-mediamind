import pytest
from fastapi.testclient import TestClient

from app.core.config import get_configs
from app.main import AppCreator

configs = get_configs()


@pytest.fixture(autouse=True)
def use_in_memory_db_and_stub_connect(monkeypatch):
    # 1) Force the DATABASE_URL to SQLite in‐memory before AppCreator runs
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")


@pytest.fixture
def client():
    # Now when we instantiate AppCreator, it will use sqlite+stubbed connect
    app_creator = AppCreator()
    app = app_creator.app

    with TestClient(app) as client:
        yield client


@pytest.fixture
def test_name(request):
    return request.node.name


@pytest.fixture(autouse=True)
def disable_auth(monkeypatch):
    """
    Force the real token-checking branch
    (so _extract_clerk_id runs verify_token).
    Otherwise the pytest won't run locally without changing it.
    """
    monkeypatch.setattr(configs, "DISABLE_AUTH", False)
