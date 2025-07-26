from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@patch("app.api.v1.endpoints.article_controller.ArticleSummaryService")
def test_summarize_all_articles_superuser(mock_summary_service):
    mock_user = MagicMock()
    mock_user.is_superuser = True

    def override_dep():
        return mock_user

    app.dependency_overrides[
        __import__(
            "app.api.v1.endpoints.article_controller",
            fromlist=["get_authenticated_user"],
        ).get_authenticated_user
    ] = override_dep
    response = client.post("/api/v1/articles/summarize-all")
    assert response.status_code == 200
    assert "Summarization started" in response.json()["message"]
    mock_summary_service.run.assert_called()
    app.dependency_overrides = {}


def test_summarize_all_articles_not_superuser():
    mock_user = MagicMock()
    mock_user.is_superuser = False
    mock_user.id = 123

    def override_dep():
        return mock_user

    app.dependency_overrides[
        __import__(
            "app.api.v1.endpoints.article_controller",
            fromlist=["get_authenticated_user"],
        ).get_authenticated_user
    ] = override_dep
    response = client.post("/api/v1/articles/summarize-all")
    assert response.status_code == 200
    assert "You do not have permission" in response.json()["message"]
    app.dependency_overrides = {}
