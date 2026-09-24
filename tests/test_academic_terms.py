from fastapi.testclient import TestClient


def _term_payload(**overrides):
    payload = {
        "academic_year": "2026",
        "semester": "5",
        "name": "Odd Semester 2026",
        "start_date": "2026-07-01",
        "end_date": "2026-12-15",
        "is_active": True,
    }
    payload.update(overrides)
    return payload


def test_academic_term_crud(client: TestClient):
    created = client.post("/api/academic-terms", json=_term_payload())
    assert created.status_code == 201
    term_id = created.json()["id"]
    assert created.json()["is_active"] is True

    listed = client.get("/api/academic-terms", params={"is_active": True})
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    updated = client.put(
        f"/api/academic-terms/{term_id}",
        json=_term_payload(name="Semester 5 2026", is_active=False),
    )
    assert updated.status_code == 200
    assert updated.json()["is_active"] is False

    deleted = client.delete(f"/api/academic-terms/{term_id}")
    assert deleted.status_code == 204


def test_duplicate_academic_term_and_invalid_dates(client: TestClient):
    first = client.post("/api/academic-terms", json=_term_payload())
    assert first.status_code == 201

    duplicate = client.post("/api/academic-terms", json=_term_payload())
    assert duplicate.status_code == 409

    invalid = client.post(
        "/api/academic-terms",
        json=_term_payload(start_date="2026-12-15", end_date="2026-07-01"),
    )
    assert invalid.status_code == 422


def test_cannot_delete_term_with_section(client: TestClient):
    department = client.post(
        "/api/departments",
        json={"name": "CSE", "code": "CSE"},
    ).json()
    program = client.post(
        "/api/programs",
        json={
            "department_id": department["id"],
            "name": "B.Tech CSE",
            "code": "BT-CSE",
        },
    ).json()
    term = client.post("/api/academic-terms", json=_term_payload()).json()
    client.post(
        "/api/sections",
        json={
            "program_id": program["id"],
            "academic_term_id": term["id"],
            "name": "A",
        },
    )

    response = client.delete(f"/api/academic-terms/{term['id']}")
    assert response.status_code == 409
