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


def _create_department(client: TestClient, code: str = "CSE") -> dict:
    return client.post(
        "/api/departments",
        json={"name": f"Department {code}", "code": code},
    ).json()


def _faculty_payload(user_id: int, department_id: int, **overrides):
    payload = {
        "user_id": user_id,
        "department_id": department_id,
        "employee_identifier": "EMP001",
        "first_name": "Ravi",
        "last_name": "Kumar",
        "is_active": True,
    }
    payload.update(overrides)
    return payload


def test_faculty_create_list_get_update(
    client: TestClient,
    db_session: Session,
):
    department = _create_department(client)
    user = _create_user(
        db_session,
        username="faculty1",
        email="faculty1@example.com",
        role="FACULTY",
    )

    created = client.post(
        "/api/faculty",
        json=_faculty_payload(user.id, department["id"]),
    )
    assert created.status_code == 201
    body = created.json()
    faculty_id = body["id"]
    assert body["employee_identifier"] == "EMP001"

    listed = client.get("/api/faculty", params={"department_id": department["id"]})
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    fetched = client.get(f"/api/faculty/{faculty_id}")
    assert fetched.status_code == 200
    assert fetched.json()["first_name"] == "Ravi"

    updated = client.put(
        f"/api/faculty/{faculty_id}",
        json=_faculty_payload(
            user.id,
            department["id"],
            first_name="Ravi S.",
            is_active=False,
        ),
    )
    assert updated.status_code == 200
    assert updated.json()["first_name"] == "Ravi S."
    assert updated.json()["is_active"] is False

    missing = client.get("/api/faculty/999")
    assert missing.status_code == 404


def test_faculty_unique_and_validation_failures(
    client: TestClient,
    db_session: Session,
):
    department = _create_department(client)
    user = _create_user(
        db_session,
        username="faculty1",
        email="faculty1@example.com",
        role="FACULTY",
    )
    other_user = _create_user(
        db_session,
        username="faculty2",
        email="faculty2@example.com",
        role="FACULTY",
    )
    student_user = _create_user(
        db_session,
        username="student1",
        email="student1@example.com",
        role="STUDENT",
    )

    payload = _faculty_payload(user.id, department["id"])
    assert client.post("/api/faculty", json=payload).status_code == 201

    duplicate_identifier = client.post(
        "/api/faculty",
        json=_faculty_payload(
            other_user.id,
            department["id"],
            employee_identifier="EMP001",
        ),
    )
    assert duplicate_identifier.status_code == 409

    duplicate_user = client.post(
        "/api/faculty",
        json=_faculty_payload(
            user.id,
            department["id"],
            employee_identifier="EMP002",
        ),
    )
    assert duplicate_user.status_code == 409

    missing_user = client.post(
        "/api/faculty",
        json=_faculty_payload(999, department["id"], employee_identifier="EMP003"),
    )
    assert missing_user.status_code == 404

    missing_department = client.post(
        "/api/faculty",
        json=_faculty_payload(other_user.id, 999, employee_identifier="EMP004"),
    )
    assert missing_department.status_code == 404

    wrong_role = client.post(
        "/api/faculty",
        json=_faculty_payload(
            student_user.id,
            department["id"],
            employee_identifier="EMP005",
        ),
    )
    assert wrong_role.status_code == 400

    invalid = client.post(
        "/api/faculty",
        json=_faculty_payload(
            other_user.id,
            department["id"],
            first_name="  ",
            employee_identifier="EMP006",
        ),
    )
    assert invalid.status_code == 422


def test_faculty_can_list_but_not_create_faculty(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    department = _create_department(client)
    user = _create_user(
        db_session,
        username="faculty1",
        email="faculty1@example.com",
        role="FACULTY",
    )
    created = client.post(
        "/api/faculty",
        json=_faculty_payload(user.id, department["id"]),
    )
    assert created.status_code == 201

    current_user_payload["role"] = "FACULTY"
    listed = client.get("/api/faculty")
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    forbidden_create = client.post(
        "/api/faculty",
        json=_faculty_payload(user.id, department["id"], employee_identifier="EMP099"),
    )
    assert forbidden_create.status_code == 403


def test_student_cannot_list_faculty(
    client: TestClient,
    current_user_payload: dict,
):
    current_user_payload["role"] = "STUDENT"
    response = client.get("/api/faculty")
    assert response.status_code == 403


def test_anonymous_cannot_list_faculty(anonymous_client: TestClient):
    response = anonymous_client.get("/api/faculty")
    assert response.status_code in (401, 403)
