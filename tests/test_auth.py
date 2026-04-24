def test_register_success(client):
    response = client.post("/auth/register", json={
        "username": "vishnuraj",
        "email": "vishnuraj@example.com",
        "password": "test1234"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "vishnuraj"
    assert data["email"] == "vishnuraj@example.com"
    assert "password" not in data  # password never exposed


def test_register_duplicate(client):
    client.post("/auth/register", json={
        "username": "vishnuraj",
        "email": "vishnuraj@example.com",
        "password": "test1234"
    })
    response = client.post("/auth/register", json={
        "username": "vishnuraj",
        "email": "vishnuraj@example.com",
        "password": "test1234"
    })
    assert response.status_code == 400


def test_login_success(client, registered_user):
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "test1234"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, registered_user):
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_get_me_success(client, auth_headers):
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_get_me_no_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401