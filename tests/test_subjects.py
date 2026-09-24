from fastapi.testclient import TestClient


def _create_department(client: TestClient, code: str = "CSE") -> dict:
    return client.post(
        "/api/departments",
        json={"name": f"Department {code}", "code": code},
    ).json()


def _subject_payload(department_id: int, **overrides):
    payload = {
        "department_id": department_id,
        "subject_code": "cs301",
        "name": "Database Management Systems",
        "credits": 4,
        "is_active": True,
    }
    payload.update(overrides)
    return payload


def test_subject_create_list_get_update_delete(client: TestClient):
    cse = _create_department(client, "CSE")
    ece = _create_department(client, "ECE")

    created = client.post("/api/subjects", json=_subject_payload(cse["id"]))
    assert created.status_code == 201
    body = created.json()
    subject_id = body["id"]
    assert body["subject_code"] == "CS301"

    client.post(
        "/api/subjects",
        json=_subject_payload(ece["id"], subject_code="EC201", name="Signals"),
    )

    filtered = client.get("/api/subjects", params={"department_id": cse["id"]})
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1
    assert filtered.json()["items"][0]["id"] == subject_id

    fetched = client.get(f"/api/subjects/{subject_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Database Management Systems"

    updated = client.put(
        f"/api/subjects/{subject_id}",
        json=_subject_payload(
            cse["id"],
            subject_code="CS301",
            name="DBMS",
            is_active=False,
        ),
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "DBMS"
    assert updated.json()["is_active"] is False

    deleted = client.delete(f"/api/subjects/{subject_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/subjects/{subject_id}").status_code == 404


def test_subject_unique_and_validation_failures(client: TestClient):
    department = _create_department(client)

    created = client.post("/api/subjects", json=_subject_payload(department["id"]))
    assert created.status_code == 201

    duplicate = client.post(
        "/api/subjects",
        json=_subject_payload(department["id"], name="Other"),
    )
    assert duplicate.status_code == 409

    missing_department = client.post(
        "/api/subjects",
        json=_subject_payload(999, subject_code="CS302"),
    )
    assert missing_department.status_code == 404

    invalid_name = client.post(
        "/api/subjects",
        json=_subject_payload(department["id"], subject_code="CS303", name="  "),
    )
    assert invalid_name.status_code == 422

    invalid_credits = client.post(
        "/api/subjects",
        json=_subject_payload(department["id"], subject_code="CS304", credits=0),
    )
    assert invalid_credits.status_code == 422

    missing = client.get("/api/subjects/999")
    assert missing.status_code == 404


def test_faculty_can_list_but_not_create_subject(
    client: TestClient,
    current_user_payload: dict,
):
    department = _create_department(client)
    created = client.post("/api/subjects", json=_subject_payload(department["id"]))
    assert created.status_code == 201

    current_user_payload["role"] = "FACULTY"
    listed = client.get("/api/subjects")
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    forbidden_create = client.post(
        "/api/subjects",
        json=_subject_payload(department["id"], subject_code="CS399"),
    )
    assert forbidden_create.status_code == 403


def test_student_cannot_list_subjects(
    client: TestClient,
    current_user_payload: dict,
):
    current_user_payload["role"] = "STUDENT"
    response = client.get("/api/subjects")
    assert response.status_code == 403


def test_anonymous_cannot_list_subjects(anonymous_client: TestClient):
    response = anonymous_client.get("/api/subjects")
    assert response.status_code in (401, 403)
