def test_create_task_success(client, auth_headers):
    response = client.post("/tasks/", json={
        "title": "Test Task",
        "description": "Test description",
        "priority": "high",
        "status": "todo"
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["priority"] == "high"
    assert data["status"] == "todo"


def test_create_task_no_auth(client):
    response = client.post("/tasks/", json={"title": "Test Task"})
    assert response.status_code == 401


def test_get_tasks_empty(client, auth_headers):
    response = client.get("/tasks/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["tasks"] == []
    assert data["total"] == 0


def test_get_tasks_returns_own_tasks_only(client):
    # Register two users
    client.post("/auth/register", json={
        "username": "user1", "email": "user1@example.com", "password": "test1234"
    })
    client.post("/auth/register", json={
        "username": "user2", "email": "user2@example.com", "password": "test1234"
    })

    # Login as user1 and create a task
    r1 = client.post("/auth/login", data={"username": "user1", "password": "test1234"})
    headers1 = {"Authorization": f"Bearer {r1.json()['access_token']}"}
    client.post("/tasks/", json={"title": "User1 Task"}, headers=headers1)

    # Login as user2 and get tasks
    r2 = client.post("/auth/login", data={"username": "user2", "password": "test1234"})
    headers2 = {"Authorization": f"Bearer {r2.json()['access_token']}"}
    response = client.get("/tasks/", headers=headers2)

    # User2 should see zero tasks
    assert response.json()["total"] == 0


def test_get_single_task(client, auth_headers):
    created = client.post("/tasks/", json={"title": "Single Task"}, headers=auth_headers)
    task_id = created.json()["id"]

    response = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Single Task"


def test_get_task_not_found(client, auth_headers):
    response = client.get("/tasks/999", headers=auth_headers)
    assert response.status_code == 404


def test_update_task(client, auth_headers):
    created = client.post("/tasks/", json={
        "title": "Old Title",
        "status": "todo"
    }, headers=auth_headers)
    task_id = created.json()["id"]

    response = client.put(f"/tasks/{task_id}", json={
        "title": "New Title",
        "status": "done"
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["status"] == "done"


def test_update_task_partial(client, auth_headers):
    created = client.post("/tasks/", json={
        "title": "My Task",
        "priority": "low"
    }, headers=auth_headers)
    task_id = created.json()["id"]

    # Only update status — title and priority should stay unchanged
    response = client.put(f"/tasks/{task_id}", json={"status": "done"}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "done"
    assert data["title"] == "My Task"
    assert data["priority"] == "low"


def test_delete_task(client, auth_headers):
    created = client.post("/tasks/", json={"title": "Delete Me"}, headers=auth_headers)
    task_id = created.json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 204

    # Confirm it is gone
    response = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 404


def test_delete_task_other_user(client):
    # User1 creates a task
    client.post("/auth/register", json={
        "username": "user1", "email": "user1@example.com", "password": "test1234"
    })
    r1 = client.post("/auth/login", data={"username": "user1", "password": "test1234"})
    headers1 = {"Authorization": f"Bearer {r1.json()['access_token']}"}
    created = client.post("/tasks/", json={"title": "User1 Task"}, headers=headers1)
    task_id = created.json()["id"]

    # User2 tries to delete user1's task
    client.post("/auth/register", json={
        "username": "user2", "email": "user2@example.com", "password": "test1234"
    })
    r2 = client.post("/auth/login", data={"username": "user2", "password": "test1234"})
    headers2 = {"Authorization": f"Bearer {r2.json()['access_token']}"}

    response = client.delete(f"/tasks/{task_id}", headers=headers2)
    assert response.status_code == 404