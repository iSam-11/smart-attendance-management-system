from fastapi.testclient import TestClient


def test_root_and_health(client: TestClient):
    root = client.get("/")
    assert root.status_code == 200
    assert root.json()["status"] == "running"

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "healthy"}


def test_create_list_get_update_delete_department(client: TestClient):
    created = client.post(
        "/api/departments",
        json={"name": "Computer Science", "code": "cse"},
    )
    assert created.status_code == 201
    body = created.json()
    assert body["code"] == "CSE"
    department_id = body["id"]

    listed = client.get("/api/departments")
    assert listed.status_code == 200
    payload = listed.json()
    assert payload["total"] == 1
    assert payload["items"][0]["id"] == department_id

    fetched = client.get(f"/api/departments/{department_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Computer Science"

    updated = client.put(
        f"/api/departments/{department_id}",
        json={"name": "Computer Science and Engineering", "code": "CSE"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Computer Science and Engineering"

    deleted = client.delete(f"/api/departments/{department_id}")
    assert deleted.status_code == 204

    missing = client.get(f"/api/departments/{department_id}")
    assert missing.status_code == 404


def test_duplicate_department_returns_conflict(client: TestClient):
    client.post("/api/departments", json={"name": "IT", "code": "IT"})
    duplicate_code = client.post(
        "/api/departments",
        json={"name": "Information Technology", "code": "IT"},
    )
    assert duplicate_code.status_code == 409

    duplicate_name = client.post(
        "/api/departments",
        json={"name": "IT", "code": "ITE"},
    )
    assert duplicate_name.status_code == 409


def test_invalid_department_payload(client: TestClient):
    response = client.post("/api/departments", json={"name": "  ", "code": "CSE"})
    assert response.status_code == 422


def test_faculty_can_list_but_not_create_department(
    client: TestClient,
    current_user_payload: dict,
):
    client.post("/api/departments", json={"name": "ECE", "code": "ECE"})

    current_user_payload["role"] = "FACULTY"
    listed = client.get("/api/departments")
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    created = client.post(
        "/api/departments",
        json={"name": "ME", "code": "ME"},
    )
    assert created.status_code == 403


def test_student_cannot_list_departments(
    client: TestClient,
    current_user_payload: dict,
):
    current_user_payload["role"] = "STUDENT"
    response = client.get("/api/departments")
    assert response.status_code == 403


def test_anonymous_cannot_list_departments(anonymous_client: TestClient):
    response = anonymous_client.get("/api/departments")
    assert response.status_code in (401, 403)


def test_cannot_delete_department_with_program(client: TestClient):
    department = client.post(
        "/api/departments",
        json={"name": "CSE", "code": "CSE"},
    ).json()
    client.post(
        "/api/programs",
        json={
            "department_id": department["id"],
            "name": "B.Tech CSE",
            "code": "BT-CSE",
        },
    )

    response = client.delete(f"/api/departments/{department['id']}")
    assert response.status_code == 409
