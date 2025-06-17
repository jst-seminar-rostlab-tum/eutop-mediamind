import pytest
from fastapi.testclient import TestClient

from app.main import AppCreator


@pytest.fixture
def client():
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
