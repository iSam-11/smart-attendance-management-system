from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.db.models.user import User


def _create_user(
    db_session: Session,
    *,
    username: str,
    email: str,
    role: str,
) -> User:
    user = User(
        username=username,
        email=email,
        password_hash="hashed-password",
        role=role,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _setup_section(client: TestClient) -> dict:
    department = client.post(
        "/api/departments",
        json={"name": "Computer Science", "code": "CSE"},
    ).json()
    other_department = client.post(
        "/api/departments",
        json={"name": "Electronics", "code": "ECE"},
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
    section = client.post(
        "/api/sections",
        json={
            "program_id": program["id"],
            "academic_term_id": term["id"],
            "name": "A",
        },
    ).json()
    return {
        "department": department,
        "other_department": other_department,
        "section": section,
    }


def _student_payload(user_id: int, department_id: int, section_id: int, **overrides):
    payload = {
        "user_id": user_id,
        "department_id": department_id,
        "section_id": section_id,
        "student_identifier": "CSE2026001",
        "enrollment_number": "ENR001",
        "first_name": "Asha",
        "last_name": "Patel",
        "date_of_birth": "2006-01-15",
        "admission_year": 2024,
        "is_active": True,
    }
    payload.update(overrides)
    return payload


def test_student_create_list_get_update(
    client: TestClient,
    db_session: Session,
):
    setup = _setup_section(client)
    user = _create_user(
        db_session,
        username="student1",
        email="student1@example.com",
        role="STUDENT",
    )

    created = client.post(
        "/api/students",
        json=_student_payload(
            user.id,
            setup["department"]["id"],
            setup["section"]["id"],
        ),
    )
    assert created.status_code == 201
    body = created.json()
    student_id = body["id"]
    assert body["student_identifier"] == "CSE2026001"
    assert body["is_active"] is True

    listed = client.get(
        "/api/students",
        params={"department_id": setup["department"]["id"]},
    )
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["id"] == student_id

    fetched = client.get(f"/api/students/{student_id}")
    assert fetched.status_code == 200
    assert fetched.json()["first_name"] == "Asha"

    updated = client.put(
        f"/api/students/{student_id}",
        json=_student_payload(
            user.id,
            setup["department"]["id"],
            setup["section"]["id"],
            first_name="Asha R.",
            is_active=False,
        ),
    )
    assert updated.status_code == 200
    assert updated.json()["first_name"] == "Asha R."
    assert updated.json()["is_active"] is False

    missing = client.get("/api/students/999")
    assert missing.status_code == 404


def test_student_unique_and_validation_failures(
    client: TestClient,
    db_session: Session,
):
    setup = _setup_section(client)
    user = _create_user(
        db_session,
        username="student1",
        email="student1@example.com",
        role="STUDENT",
    )
    other_user = _create_user(
        db_session,
        username="student2",
        email="student2@example.com",
        role="STUDENT",
    )
    faculty_user = _create_user(
        db_session,
        username="faculty1",
        email="faculty1@example.com",
        role="FACULTY",
    )

    payload = _student_payload(
        user.id,
        setup["department"]["id"],
        setup["section"]["id"],
    )
    assert client.post("/api/students", json=payload).status_code == 201

    duplicate_identifier = client.post(
        "/api/students",
        json=_student_payload(
            other_user.id,
            setup["department"]["id"],
            setup["section"]["id"],
            student_identifier="CSE2026001",
            enrollment_number="ENR002",
        ),
    )
    assert duplicate_identifier.status_code == 409

    duplicate_enrollment = client.post(
        "/api/students",
        json=_student_payload(
            other_user.id,
            setup["department"]["id"],
            setup["section"]["id"],
            student_identifier="CSE2026002",
            enrollment_number="ENR001",
        ),
    )
    assert duplicate_enrollment.status_code == 409

    duplicate_user = client.post(
        "/api/students",
        json=_student_payload(
            user.id,
            setup["department"]["id"],
            setup["section"]["id"],
            student_identifier="CSE2026003",
            enrollment_number="ENR003",
        ),
    )
    assert duplicate_user.status_code == 409

    missing_user = client.post(
        "/api/students",
        json=_student_payload(
            999,
            setup["department"]["id"],
            setup["section"]["id"],
            student_identifier="CSE2026004",
            enrollment_number="ENR004",
        ),
    )
    assert missing_user.status_code == 404

    wrong_role = client.post(
        "/api/students",
        json=_student_payload(
            faculty_user.id,
            setup["department"]["id"],
            setup["section"]["id"],
            student_identifier="CSE2026005",
            enrollment_number="ENR005",
        ),
    )
    assert wrong_role.status_code == 400

    mismatched_department = client.post(
        "/api/students",
        json=_student_payload(
            other_user.id,
            setup["other_department"]["id"],
            setup["section"]["id"],
            student_identifier="CSE2026006",
            enrollment_number="ENR006",
        ),
    )
    assert mismatched_department.status_code == 400

    missing_section = client.post(
        "/api/students",
        json=_student_payload(
            other_user.id,
            setup["department"]["id"],
            999,
            student_identifier="CSE2026007",
            enrollment_number="ENR007",
        ),
    )
    assert missing_section.status_code == 404

    invalid = client.post(
        "/api/students",
        json=_student_payload(
            other_user.id,
            setup["department"]["id"],
            setup["section"]["id"],
            first_name="  ",
            student_identifier="CSE2026008",
            enrollment_number="ENR008",
        ),
    )
    assert invalid.status_code == 422


def test_faculty_can_list_but_not_create_student(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_section(client)
    user = _create_user(
        db_session,
        username="student1",
        email="student1@example.com",
        role="STUDENT",
    )
    created = client.post(
        "/api/students",
        json=_student_payload(
            user.id,
            setup["department"]["id"],
            setup["section"]["id"],
        ),
    )
    assert created.status_code == 201

    current_user_payload["role"] = "FACULTY"
    listed = client.get("/api/students")
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    forbidden_create = client.post(
        "/api/students",
        json=_student_payload(
            user.id,
            setup["department"]["id"],
            setup["section"]["id"],
            student_identifier="CSE2026099",
            enrollment_number="ENR099",
        ),
    )
    assert forbidden_create.status_code == 403


def test_student_cannot_list_students(
    client: TestClient,
    current_user_payload: dict,
):
    current_user_payload["role"] = "STUDENT"
    response = client.get("/api/students")
    assert response.status_code == 403


def test_anonymous_cannot_list_students(anonymous_client: TestClient):
    response = anonymous_client.get("/api/students")
    assert response.status_code in (401, 403)
