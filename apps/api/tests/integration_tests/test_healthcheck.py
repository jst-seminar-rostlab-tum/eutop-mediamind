from fastapi.testclient import TestClient


def test_healthcheck(client: TestClient):
    response = client.get("/api/v1/healthcheck")
    assert response.status_code == 200
    body = response.json()
    assert body == {"status": "ok"}
