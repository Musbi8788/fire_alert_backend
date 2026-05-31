def test_healthz_returns_ok(client):
    response = client.get("/api/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_home_returns_welcome(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert "message" in body
    assert "timestamp" in body
