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


def _setup_assignment_dependencies(
    client: TestClient,
    db_session: Session,
    suffix: str | None = None,
) -> dict:
    if suffix is None:
        suffix = uuid.uuid4().hex[:6]

    code = f"FA{suffix[:4]}".upper()
    dept = client.post(
        "/api/departments",
        json={"name": f"Dept {suffix}", "code": code},
    ).json()

    other_dept = client.post(
        "/api/departments",
        json={"name": f"Other Dept {suffix}", "code": f"O{code}"},
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
            "name": "Software Engineering",
            "credits": 4,
            "is_active": True,
        },
    ).json()

    fac_user = _create_user(
        db_session,
        username=f"fac_user_{suffix}",
        email=f"fac_user_{suffix}@example.com",
        role="FACULTY",
    )

    faculty = client.post(
        "/api/faculty",
        json={
            "user_id": fac_user.id,
            "department_id": dept["id"],
            "employee_identifier": f"EMP_{suffix}".upper(),
            "first_name": "Anita",
            "last_name": "Roy",
            "is_active": True,
        },
    ).json()

    return {
        "department": dept,
        "other_department": other_dept,
        "program": program,
        "term": term,
        "section": section,
        "subject": subject,
        "faculty_user": fac_user,
        "faculty": faculty,
    }


def test_faculty_assignment_crud_and_filters(
    client: TestClient,
    db_session: Session,
):
    setup = _setup_assignment_dependencies(client, db_session)

    payload = {
        "faculty_id": setup["faculty"]["id"],
        "subject_id": setup["subject"]["id"],
        "section_id": setup["section"]["id"],
        "academic_term_id": setup["term"]["id"],
    }

    # Creation
    created = client.post("/api/faculty-assignments", json=payload)
    assert created.status_code == 201
    body = created.json()
    assignment_id = body["id"]
    assert body["faculty_id"] == setup["faculty"]["id"]
    assert body["subject_id"] == setup["subject"]["id"]

    # List & Filter
    listed = client.get("/api/faculty-assignments")
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["id"] == assignment_id

    filtered = client.get(
        "/api/faculty-assignments",
        params={"faculty_id": setup["faculty"]["id"], "subject_id": setup["subject"]["id"]},
    )
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1

    # Get by ID
    fetched = client.get(f"/api/faculty-assignments/{assignment_id}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == assignment_id

    # Update
    updated = client.put(f"/api/faculty-assignments/{assignment_id}", json=payload)
    assert updated.status_code == 200
    assert updated.json()["id"] == assignment_id

    # Delete
    deleted = client.delete(f"/api/faculty-assignments/{assignment_id}")
    assert deleted.status_code == 204

    # Verify deleted
    missing = client.get(f"/api/faculty-assignments/{assignment_id}")
    assert missing.status_code == 404


def test_duplicate_faculty_assignment(
    client: TestClient,
    db_session: Session,
):
    setup = _setup_assignment_dependencies(client, db_session)
    payload = {
        "faculty_id": setup["faculty"]["id"],
        "subject_id": setup["subject"]["id"],
        "section_id": setup["section"]["id"],
        "academic_term_id": setup["term"]["id"],
    }

    assert client.post("/api/faculty-assignments", json=payload).status_code == 201
    duplicate = client.post("/api/faculty-assignments", json=payload)
    assert duplicate.status_code == 409


def test_missing_relations_for_faculty_assignment(
    client: TestClient,
    db_session: Session,
):
    setup = _setup_assignment_dependencies(client, db_session)

    # Missing faculty
    res = client.post(
        "/api/faculty-assignments",
        json={
            "faculty_id": 9999,
            "subject_id": setup["subject"]["id"],
            "section_id": setup["section"]["id"],
            "academic_term_id": setup["term"]["id"],
        },
    )
    assert res.status_code == 404
    assert "Faculty not found" in res.json()["detail"]

    # Missing subject
    res = client.post(
        "/api/faculty-assignments",
        json={
            "faculty_id": setup["faculty"]["id"],
            "subject_id": 9999,
            "section_id": setup["section"]["id"],
            "academic_term_id": setup["term"]["id"],
        },
    )
    assert res.status_code == 404
    assert "Subject not found" in res.json()["detail"]

    # Missing section
    res = client.post(
        "/api/faculty-assignments",
        json={
            "faculty_id": setup["faculty"]["id"],
            "subject_id": setup["subject"]["id"],
            "section_id": 9999,
            "academic_term_id": setup["term"]["id"],
        },
    )
    assert res.status_code == 404
    assert "Section not found" in res.json()["detail"]

    # Missing academic term
    res = client.post(
        "/api/faculty-assignments",
        json={
            "faculty_id": setup["faculty"]["id"],
            "subject_id": setup["subject"]["id"],
            "section_id": setup["section"]["id"],
            "academic_term_id": 9999,
        },
    )
    assert res.status_code == 404
    assert "Academic term not found" in res.json()["detail"]


def test_inactive_and_compatibility_validations(
    client: TestClient,
    db_session: Session,
):
    setup = _setup_assignment_dependencies(client, db_session)

    # Inactive faculty
    inact_user = _create_user(
        db_session,
        username="inact_fac_user",
        email="inact_fac_user@example.com",
        role="FACULTY",
    )
    inact_faculty = client.post(
        "/api/faculty",
        json={
            "user_id": inact_user.id,
            "department_id": setup["department"]["id"],
            "employee_identifier": "EMP_INACT_1",
            "first_name": "Inact",
            "last_name": "Faculty",
            "is_active": False,
        },
    ).json()

    res = client.post(
        "/api/faculty-assignments",
        json={
            "faculty_id": inact_faculty["id"],
            "subject_id": setup["subject"]["id"],
            "section_id": setup["section"]["id"],
            "academic_term_id": setup["term"]["id"],
        },
    )
    assert res.status_code == 400
    assert "Faculty is not active" in res.json()["detail"]

    # Inactive subject
    inact_subject = client.post(
        "/api/subjects",
        json={
            "department_id": setup["department"]["id"],
            "subject_code": "CSINACT99",
            "name": "Inactive Subj",
            "credits": 3,
            "is_active": False,
        },
    ).json()

    res = client.post(
        "/api/faculty-assignments",
        json={
            "faculty_id": setup["faculty"]["id"],
            "subject_id": inact_subject["id"],
            "section_id": setup["section"]["id"],
            "academic_term_id": setup["term"]["id"],
        },
    )
    assert res.status_code == 400
    assert "Subject is not active" in res.json()["detail"]

    # Inactive term
    inact_term = client.post(
        "/api/academic-terms",
        json={
            "academic_year": "2028",
            "semester": "8",
            "name": "Term 2028 Inactive",
            "start_date": "2028-01-01",
            "end_date": "2028-05-31",
            "is_active": False,
        },
    ).json()

    inact_term_sec = client.post(
        "/api/sections",
        json={
            "program_id": setup["program"]["id"],
            "academic_term_id": inact_term["id"],
            "name": "Sec-InactTerm",
        },
    ).json()

    res = client.post(
        "/api/faculty-assignments",
        json={
            "faculty_id": setup["faculty"]["id"],
            "subject_id": setup["subject"]["id"],
            "section_id": inact_term_sec["id"],
            "academic_term_id": inact_term["id"],
        },
    )
    assert res.status_code == 400
    assert "Academic term is not active" in res.json()["detail"]

    # Section mismatch with academic term
    other_term = client.post(
        "/api/academic-terms",
        json={
            "academic_year": "2026",
            "semester": "6",
            "name": "Other Active Term 2026",
            "start_date": "2026-01-01",
            "end_date": "2026-05-31",
            "is_active": True,
        },
    ).json()

    res = client.post(
        "/api/faculty-assignments",
        json={
            "faculty_id": setup["faculty"]["id"],
            "subject_id": setup["subject"]["id"],
            "section_id": setup["section"]["id"],
            "academic_term_id": other_term["id"],
        },
    )
    assert res.status_code == 400
    assert "Section does not belong to the selected academic term" in res.json()["detail"]

    # Faculty department mismatch with subject department
    other_dept_fac_user = _create_user(
        db_session,
        username="other_dept_fac",
        email="other_dept_fac@example.com",
        role="FACULTY",
    )
    other_dept_faculty = client.post(
        "/api/faculty",
        json={
            "user_id": other_dept_fac_user.id,
            "department_id": setup["other_department"]["id"],
            "employee_identifier": "EMP_OTH_DEPT",
            "first_name": "Suresh",
            "last_name": "Rao",
            "is_active": True,
        },
    ).json()

    res = client.post(
        "/api/faculty-assignments",
        json={
            "faculty_id": other_dept_faculty["id"],
            "subject_id": setup["subject"]["id"],
            "section_id": setup["section"]["id"],
            "academic_term_id": setup["term"]["id"],
        },
    )
    assert res.status_code == 400
    assert "Faculty does not belong to the subject's department" in res.json()["detail"]


def test_authorization_and_authentication(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_assignment_dependencies(client, db_session)
    payload = {
        "faculty_id": setup["faculty"]["id"],
        "subject_id": setup["subject"]["id"],
        "section_id": setup["section"]["id"],
        "academic_term_id": setup["term"]["id"],
    }

    # Faculty user can list/get, but not create/update/delete
    current_user_payload["role"] = "FACULTY"
    listed = client.get("/api/faculty-assignments")
    assert listed.status_code == 200

    forbidden_create = client.post("/api/faculty-assignments", json=payload)
    assert forbidden_create.status_code == 403

    forbidden_update = client.put("/api/faculty-assignments/1", json=payload)
    assert forbidden_update.status_code == 403

    forbidden_delete = client.delete("/api/faculty-assignments/1")
    assert forbidden_delete.status_code == 403

    # Student user cannot list or manage
    current_user_payload["role"] = "STUDENT"
    forbidden_list = client.get("/api/faculty-assignments")
    assert forbidden_list.status_code == 403

    forbidden_create_stu = client.post("/api/faculty-assignments", json=payload)
    assert forbidden_create_stu.status_code == 403


def test_anonymous_cannot_list_assignments(anonymous_client: TestClient):
    res = anonymous_client.get("/api/faculty-assignments")
    assert res.status_code in (401, 403)
