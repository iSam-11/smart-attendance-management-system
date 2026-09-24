from fastapi.testclient import TestClient


def _setup_program_and_term(client: TestClient) -> tuple[dict, dict]:
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
    term = client.post(
        "/api/academic-terms",
        json={
            "academic_year": "2026",
            "semester": "5",
            "name": "Odd Semester 2026",
            "start_date": "2026-07-01",
            "end_date": "2026-12-15",
            "is_active": True,
        },
    ).json()
    return program, term


def test_section_crud_and_filters(client: TestClient):
    program, term = _setup_program_and_term(client)
    created = client.post(
        "/api/sections",
        json={
            "program_id": program["id"],
            "academic_term_id": term["id"],
            "name": "A",
        },
    )
    assert created.status_code == 201
    section_id = created.json()["id"]

    listed = client.get(
        "/api/sections",
        params={"program_id": program["id"], "academic_term_id": term["id"]},
    )
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    updated = client.put(
        f"/api/sections/{section_id}",
        json={
            "program_id": program["id"],
            "academic_term_id": term["id"],
            "name": "B",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "B"

    deleted = client.delete(f"/api/sections/{section_id}")
    assert deleted.status_code == 204


def test_section_duplicate_and_missing_parents(client: TestClient):
    program, term = _setup_program_and_term(client)
    payload = {
        "program_id": program["id"],
        "academic_term_id": term["id"],
        "name": "A",
    }
    assert client.post("/api/sections", json=payload).status_code == 201
    assert client.post("/api/sections", json=payload).status_code == 409

    missing_program = client.post(
        "/api/sections",
        json={"program_id": 999, "academic_term_id": term["id"], "name": "C"},
    )
    assert missing_program.status_code == 404

    missing_term = client.post(
        "/api/sections",
        json={"program_id": program["id"], "academic_term_id": 999, "name": "C"},
    )
    assert missing_term.status_code == 404


def test_cannot_delete_program_with_section(client: TestClient):
    program, term = _setup_program_and_term(client)
    client.post(
        "/api/sections",
        json={
            "program_id": program["id"],
            "academic_term_id": term["id"],
            "name": "A",
        },
    )
    response = client.delete(f"/api/programs/{program['id']}")
    assert response.status_code == 409
