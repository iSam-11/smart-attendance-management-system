from fastapi.testclient import TestClient


def _create_department(client: TestClient, code: str = "CSE") -> dict:
    return client.post(
        "/api/departments",
        json={"name": f"Department {code}", "code": code},
    ).json()


def test_program_crud_and_filters(client: TestClient):
    cse = _create_department(client, "CSE")
    ece = _create_department(client, "ECE")

    created = client.post(
        "/api/programs",
        json={"department_id": cse["id"], "name": "B.Tech CSE", "code": "bt-cse"},
    )
    assert created.status_code == 201
    assert created.json()["code"] == "BT-CSE"
    program_id = created.json()["id"]

    client.post(
        "/api/programs",
        json={"department_id": ece["id"], "name": "B.Tech ECE", "code": "BT-ECE"},
    )

    filtered = client.get("/api/programs", params={"department_id": cse["id"]})
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1
    assert filtered.json()["items"][0]["id"] == program_id

    updated = client.put(
        f"/api/programs/{program_id}",
        json={
            "department_id": cse["id"],
            "name": "Bachelor of Technology CSE",
            "code": "BT-CSE",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Bachelor of Technology CSE"

    deleted = client.delete(f"/api/programs/{program_id}")
    assert deleted.status_code == 204


def test_program_requires_existing_department_and_unique_code(client: TestClient):
    department = _create_department(client)
    missing = client.post(
        "/api/programs",
        json={"department_id": 999, "name": "B.Tech", "code": "BT"},
    )
    assert missing.status_code == 404

    client.post(
        "/api/programs",
        json={"department_id": department["id"], "name": "B.Tech CSE", "code": "BT-CSE"},
    )
    duplicate = client.post(
        "/api/programs",
        json={"department_id": department["id"], "name": "Other", "code": "BT-CSE"},
    )
    assert duplicate.status_code == 409


def test_faculty_cannot_create_program(
    client: TestClient,
    current_user_payload: dict,
):
    department = _create_department(client)
    current_user_payload["role"] = "FACULTY"
    response = client.post(
        "/api/programs",
        json={"department_id": department["id"], "name": "B.Tech", "code": "BT"},
    )
    assert response.status_code == 403
