import os
import pytest
from fastapi.testclient import TestClient

from app.core.config import configs
from app.main import AppCreator
import app.core.db as db_module

@pytest.fixture(autouse=True)
def use_in_memory_db_and_stub_connect(monkeypatch):
    # 1) Force the DATABASE_URL to SQLite in‐memory before AppCreator runs
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

    # 2) Stub out your real connect/disconnect hooks so no TCP is attempted
    async def noop_connect(*args, **kwargs):
        return None

    async def noop_disconnect(*args, **kwargs):
        return None

    monkeypatch.setattr(db_module, "connect", noop_connect)
    monkeypatch.setattr(db_module, "disconnect", noop_disconnect)

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
def use_sqlite_in_tests(monkeypatch):
    # Before AppCreator is instantiated, force a sqlite URL
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

@pytest.fixture(autouse=True)
def disable_auth(monkeypatch):
    """
    Force the real token-checking branch (so _extract_clerk_id runs verify_token).
    Otherwise the pytest won't run locally without changing it.
    """
    monkeypatch.setattr(configs, "DISABLE_AUTH", False)
