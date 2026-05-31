def test_register_returns_token_and_profile(client):
    response = client.post(
        "/api/users/register",
        json={
            "username": "alice",
            "password": "secret123",
            "fullName": "Alice Jallow",
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["token"]
    assert body["user"]["username"] == "alice"
    assert body["user"]["fullName"] == "Alice Jallow"
    assert body["user"]["isAdmin"] is False


def test_register_duplicate_username_conflicts(client):
    payload = {
        "username": "bob",
        "password": "secret123",
        "fullName": "Bob Ceesay",
    }
    first = client.post("/api/users/register", json=payload)
    assert first.status_code == 201

    second = client.post("/api/users/register", json=payload)
    assert second.status_code == 409


def test_register_rejects_short_password(client):
    response = client.post(
        "/api/users/register",
        json={"username": "carol", "password": "123", "fullName": "Carol"},
    )
    # Fails Pydantic validation (password min_length=6) before hitting the DB.
    assert response.status_code == 422


def test_login_succeeds_with_correct_credentials(client):
    client.post(
        "/api/users/register",
        json={"username": "dan", "password": "secret123", "fullName": "Dan"},
    )
    response = client.post(
        "/api/users/login",
        json={"username": "dan", "password": "secret123"},
    )
    assert response.status_code == 200
    assert response.json()["token"]


def test_login_fails_with_wrong_password(client):
    client.post(
        "/api/users/register",
        json={"username": "erin", "password": "secret123", "fullName": "Erin"},
    )
    response = client.post(
        "/api/users/login",
        json={"username": "erin", "password": "wrongpass"},
    )
    assert response.status_code == 401
