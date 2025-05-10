from fastapi.testclient import TestClient

def test_sign_up_and_sign_in(client: TestClient):
    # Act
    response = client.get("/api/v1/users")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body == "hello world"
