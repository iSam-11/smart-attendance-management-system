import uuid
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


def _setup_session_dependencies(
    client: TestClient,
    db_session: Session,
    suffix: str | None = None,
) -> dict:
    if suffix is None:
        suffix = uuid.uuid4().hex[:6]

    code = f"AS{suffix[:4]}".upper()
    dept = client.post(
        "/api/departments",
        json={"name": f"Dept {suffix}", "code": code},
    ).json()

    program = client.post(
        "/api/programs",
        json={
            "department_id": dept["id"],
            "name": f"B.Tech {suffix}",
            "code": f"BT-{code}",
        },
    ).json()

    term = client.post(
        "/api/academic-terms",
        json={
            "academic_year": "2026",
            "semester": "5",
            "name": f"Term {suffix}",
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
            "name": f"Sec-{suffix}",
        },
    ).json()

    subject = client.post(
        "/api/subjects",
        json={
            "department_id": dept["id"],
            "subject_code": f"SUBJ-{suffix}".upper(),
            "name": "Database Systems",
            "credits": 4,
            "is_active": True,
        },
    ).json()

    fac_user_1 = _create_user(
        db_session,
        username=f"fac_user1_{suffix}",
        email=f"fac_user1_{suffix}@example.com",
        role="FACULTY",
    )

    faculty_1 = client.post(
        "/api/faculty",
        json={
            "user_id": fac_user_1.id,
            "department_id": dept["id"],
            "employee_identifier": f"EMP1_{suffix}".upper(),
            "first_name": "Faculty",
            "last_name": "One",
            "is_active": True,
        },
    ).json()

    fac_user_2 = _create_user(
        db_session,
        username=f"fac_user2_{suffix}",
        email=f"fac_user2_{suffix}@example.com",
        role="FACULTY",
    )

    faculty_2 = client.post(
        "/api/faculty",
        json={
            "user_id": fac_user_2.id,
            "department_id": dept["id"],
            "employee_identifier": f"EMP2_{suffix}".upper(),
            "first_name": "Faculty",
            "last_name": "Two",
            "is_active": True,
        },
    ).json()

    assignment_1 = client.post(
        "/api/faculty-assignments",
        json={
            "faculty_id": faculty_1["id"],
            "subject_id": subject["id"],
            "section_id": section["id"],
            "academic_term_id": term["id"],
        },
    ).json()

    assignment_2 = client.post(
        "/api/faculty-assignments",
        json={
            "faculty_id": faculty_2["id"],
            "subject_id": subject["id"],
            "section_id": section["id"],
            "academic_term_id": term["id"],
        },
    ).json()

    student_user = _create_user(
        db_session,
        username=f"stu_user_{suffix}",
        email=f"stu_user_{suffix}@example.com",
        role="STUDENT",
    )

    return {
        "department": dept,
        "program": program,
        "term": term,
        "section": section,
        "subject": subject,
        "faculty_user_1": fac_user_1,
        "faculty_1": faculty_1,
        "faculty_user_2": fac_user_2,
        "faculty_2": faculty_2,
        "assignment_1": assignment_1,
        "assignment_2": assignment_2,
        "student_user": student_user,
    }


def test_admin_can_create_attendance_session(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    current_user_payload["role"] = "ADMIN"
    setup = _setup_session_dependencies(client, db_session)

    payload = {
        "faculty_assignment_id": setup["assignment_1"]["id"],
        "session_date": "2026-09-25",
        "start_time": "09:00:00",
        "end_time": "10:00:00",
        "topic": "Introduction to Databases",
        "status": "OPEN",
    }

    response = client.post("/api/attendance-sessions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["faculty_assignment_id"] == setup["assignment_1"]["id"]
    assert data["session_date"] == "2026-09-25"
    assert data["start_time"] == "09:00:00"
    assert data["end_time"] == "10:00:00"
    assert data["topic"] == "Introduction to Databases"


def test_assigned_faculty_can_create_session(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_session_dependencies(client, db_session)

    current_user_payload["role"] = "FACULTY"
    current_user_payload["sub"] = str(setup["faculty_user_1"].id)

    payload = {
        "faculty_assignment_id": setup["assignment_1"]["id"],
        "session_date": "2026-09-25",
        "start_time": "10:00:00",
        "end_time": "11:00:00",
        "topic": "ER Diagrams",
    }

    response = client.post("/api/attendance-sessions", json=payload)
    assert response.status_code == 201
    assert response.json()["faculty_assignment_id"] == setup["assignment_1"]["id"]


def test_faculty_cannot_create_for_another_faculty_assignment(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_session_dependencies(client, db_session)

    # Faculty 1 trying to create session for Faculty 2's assignment
    current_user_payload["role"] = "FACULTY"
    current_user_payload["sub"] = str(setup["faculty_user_1"].id)

    payload = {
        "faculty_assignment_id": setup["assignment_2"]["id"],
        "session_date": "2026-09-25",
        "start_time": "11:00:00",
        "end_time": "12:00:00",
    }

    response = client.post("/api/attendance-sessions", json=payload)
    assert response.status_code == 403
    assert "another faculty" in response.json()["detail"].lower()


def test_student_cannot_create_session(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_session_dependencies(client, db_session)

    current_user_payload["role"] = "STUDENT"
    current_user_payload["sub"] = str(setup["student_user"].id)

    payload = {
        "faculty_assignment_id": setup["assignment_1"]["id"],
        "session_date": "2026-09-25",
        "start_time": "09:00:00",
    }

    response = client.post("/api/attendance-sessions", json=payload)
    assert response.status_code == 403


def test_anonymous_cannot_create_session(
    anonymous_client: TestClient,
):
    payload = {
        "faculty_assignment_id": 1,
        "session_date": "2026-09-25",
        "start_time": "09:00:00",
    }

    response = anonymous_client.post("/api/attendance-sessions", json=payload)
    assert response.status_code in (401, 403)


def test_missing_faculty_assignment(
    client: TestClient,
    current_user_payload: dict,
):
    current_user_payload["role"] = "ADMIN"

    payload = {
        "faculty_assignment_id": 99999,
        "session_date": "2026-09-25",
        "start_time": "09:00:00",
    }

    response = client.post("/api/attendance-sessions", json=payload)
    assert response.status_code == 404
    assert "Faculty assignment not found" in response.json()["detail"]


def test_duplicate_session_rejected(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    current_user_payload["role"] = "ADMIN"
    setup = _setup_session_dependencies(client, db_session)

    payload = {
        "faculty_assignment_id": setup["assignment_1"]["id"],
        "session_date": "2026-09-25",
        "start_time": "09:00:00",
        "end_time": "10:00:00",
    }

    res1 = client.post("/api/attendance-sessions", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/attendance-sessions", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"].lower()


def test_invalid_time_range_rejected(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    current_user_payload["role"] = "ADMIN"
    setup = _setup_session_dependencies(client, db_session)

    payload = {
        "faculty_assignment_id": setup["assignment_1"]["id"],
        "session_date": "2026-09-25",
        "start_time": "10:00:00",
        "end_time": "09:00:00",  # end_time before start_time
    }

    response = client.post("/api/attendance-sessions", json=payload)
    assert response.status_code == 400
    assert "end_time must be later than start_time" in response.json()["detail"]


def test_get_and_list_authorization(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    current_user_payload["role"] = "ADMIN"
    setup = _setup_session_dependencies(client, db_session)

    # Admin creates session 1 for Assignment 1 (Faculty 1)
    s1 = client.post(
        "/api/attendance-sessions",
        json={
            "faculty_assignment_id": setup["assignment_1"]["id"],
            "session_date": "2026-09-25",
            "start_time": "09:00:00",
        },
    ).json()

    # Admin creates session 2 for Assignment 2 (Faculty 2)
    s2 = client.post(
        "/api/attendance-sessions",
        json={
            "faculty_assignment_id": setup["assignment_2"]["id"],
            "session_date": "2026-09-25",
            "start_time": "10:00:00",
        },
    ).json()

    # Admin lists all sessions
    current_user_payload["role"] = "ADMIN"
    admin_list = client.get("/api/attendance-sessions")
    assert admin_list.status_code == 200
    assert admin_list.json()["total"] == 2

    # Faculty 1 lists sessions (should only see session 1)
    current_user_payload["role"] = "FACULTY"
    current_user_payload["sub"] = str(setup["faculty_user_1"].id)
    fac1_list = client.get("/api/attendance-sessions")
    assert fac1_list.status_code == 200
    assert fac1_list.json()["total"] == 1
    assert fac1_list.json()["items"][0]["id"] == s1["id"]

    # Faculty 1 can get session 1
    fac1_get_s1 = client.get(f"/api/attendance-sessions/{s1['id']}")
    assert fac1_get_s1.status_code == 200

    # Faculty 1 cannot get session 2 (Faculty 2's session)
    fac1_get_s2 = client.get(f"/api/attendance-sessions/{s2['id']}")
    assert fac1_get_s2.status_code == 403

    # Student cannot list sessions
    current_user_payload["role"] = "STUDENT"
    current_user_payload["sub"] = str(setup["student_user"].id)
    stu_list = client.get("/api/attendance-sessions")
    assert stu_list.status_code == 403


def test_update_authorization_and_validations(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    current_user_payload["role"] = "ADMIN"
    setup = _setup_session_dependencies(client, db_session)

    session = client.post(
        "/api/attendance-sessions",
        json={
            "faculty_assignment_id": setup["assignment_1"]["id"],
            "session_date": "2026-09-25",
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "topic": "Initial Topic",
        },
    ).json()

    # Faculty 1 can update session 1
    current_user_payload["role"] = "FACULTY"
    current_user_payload["sub"] = str(setup["faculty_user_1"].id)

    update_payload = {
        "session_date": "2026-09-25",
        "start_time": "09:30:00",
        "end_time": "10:30:00",
        "topic": "Updated Topic",
        "status": "OPEN",
    }
    res = client.put(f"/api/attendance-sessions/{session['id']}", json=update_payload)
    assert res.status_code == 200
    assert res.json()["topic"] == "Updated Topic"
    assert res.json()["start_time"] == "09:30:00"

    # Faculty 2 cannot update session 1
    current_user_payload["sub"] = str(setup["faculty_user_2"].id)
    res_forb = client.put(f"/api/attendance-sessions/{session['id']}", json=update_payload)
    assert res_forb.status_code == 403
