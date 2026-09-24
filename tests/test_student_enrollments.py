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


def _setup_enrollment_dependencies(
    client: TestClient,
    db_session: Session,
    suffix: str | None = None,
) -> dict:
    if suffix is None:
        suffix = uuid.uuid4().hex[:6]

    code = f"C{suffix[:4]}".upper()
    dept_res = client.post(
        "/api/departments",
        json={"name": f"Computer Science {suffix}", "code": code},
    )
    assert dept_res.status_code == 201, f"Dept creation failed: {dept_res.status_code} {dept_res.text}"
    dept = dept_res.json()

    prog_res = client.post(
        "/api/programs",
        json={
            "department_id": dept["id"],
            "name": f"B.Tech CSE {suffix}",
            "code": f"BT-{code}",
        },
    )
    assert prog_res.status_code == 201, f"Program creation failed: {prog_res.status_code} {prog_res.text}"
    program = prog_res.json()

    term_res = client.post(
        "/api/academic-terms",
        json={
            "academic_year": "2026",
            "semester": "5",
            "name": f"Odd Semester 2026 {suffix}",
            "start_date": "2026-07-01",
            "end_date": "2026-12-15",
            "is_active": True,
        },
    )
    assert term_res.status_code == 201, f"Term creation failed: {term_res.status_code} {term_res.text}"
    term = term_res.json()

    sec_res = client.post(
        "/api/sections",
        json={
            "program_id": program["id"],
            "academic_term_id": term["id"],
            "name": f"Sec-{suffix}",
        },
    )
    assert sec_res.status_code == 201, f"Section creation failed: {sec_res.status_code} {sec_res.text}"
    section = sec_res.json()

    subj_res = client.post(
        "/api/subjects",
        json={
            "department_id": dept["id"],
            "subject_code": f"SUBJ-{suffix}".upper(),
            "name": "Data Structures",
            "credits": 4,
            "is_active": True,
        },
    )
    assert subj_res.status_code == 201, f"Subject creation failed: {subj_res.status_code} {subj_res.text}"
    subject = subj_res.json()

    student_user = _create_user(
        db_session,
        username=f"student_enr_{suffix}",
        email=f"student_enr_{suffix}@example.com",
        role="STUDENT",
    )

    stu_res = client.post(
        "/api/students",
        json={
            "user_id": student_user.id,
            "department_id": dept["id"],
            "section_id": section["id"],
            "student_identifier": f"STU_{suffix}".upper(),
            "enrollment_number": f"ENR_{suffix}".upper(),
            "first_name": "Rohan",
            "last_name": "Sharma",
            "admission_year": 2024,
            "is_active": True,
        },
    )
    assert stu_res.status_code == 201, f"Student creation failed: {stu_res.status_code} {stu_res.text}"
    student = stu_res.json()

    return {
        "department": dept,
        "program": program,
        "term": term,
        "section": section,
        "subject": subject,
        "student_user": student_user,
        "student": student,
    }


def test_student_enrollment_crud_and_filters(
    client: TestClient,
    db_session: Session,
):
    setup = _setup_enrollment_dependencies(client, db_session)

    payload = {
        "student_id": setup["student"]["id"],
        "subject_id": setup["subject"]["id"],
        "section_id": setup["section"]["id"],
        "academic_term_id": setup["term"]["id"],
    }

    # Successful creation
    created = client.post("/api/student-enrollments", json=payload)
    assert created.status_code == 201
    body = created.json()
    enrollment_id = body["id"]
    assert body["student_id"] == setup["student"]["id"]
    assert body["subject_id"] == setup["subject"]["id"]
    assert body["section_id"] == setup["section"]["id"]
    assert body["academic_term_id"] == setup["term"]["id"]

    # List enrollments
    listed = client.get("/api/student-enrollments")
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["id"] == enrollment_id

    # Filtered list
    filtered = client.get(
        "/api/student-enrollments",
        params={"student_id": setup["student"]["id"], "subject_id": setup["subject"]["id"]},
    )
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1

    # Get enrollment
    fetched = client.get(f"/api/student-enrollments/{enrollment_id}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == enrollment_id

    # Delete enrollment
    deleted = client.delete(f"/api/student-enrollments/{enrollment_id}")
    assert deleted.status_code == 204

    # Verify deleted
    missing = client.get(f"/api/student-enrollments/{enrollment_id}")
    assert missing.status_code == 404


def test_duplicate_student_enrollment(
    client: TestClient,
    db_session: Session,
):
    setup = _setup_enrollment_dependencies(client, db_session)

    payload = {
        "student_id": setup["student"]["id"],
        "subject_id": setup["subject"]["id"],
        "section_id": setup["section"]["id"],
        "academic_term_id": setup["term"]["id"],
    }

    first = client.post("/api/student-enrollments", json=payload)
    assert first.status_code == 201

    duplicate = client.post("/api/student-enrollments", json=payload)
    assert duplicate.status_code == 409


def test_missing_relations_for_enrollment(
    client: TestClient,
    db_session: Session,
):
    setup = _setup_enrollment_dependencies(client, db_session)

    # Missing student
    res = client.post(
        "/api/student-enrollments",
        json={
            "student_id": 9999,
            "subject_id": setup["subject"]["id"],
            "section_id": setup["section"]["id"],
            "academic_term_id": setup["term"]["id"],
        },
    )
    assert res.status_code == 404
    assert "Student not found" in res.json()["detail"]

    # Missing subject
    res = client.post(
        "/api/student-enrollments",
        json={
            "student_id": setup["student"]["id"],
            "subject_id": 9999,
            "section_id": setup["section"]["id"],
            "academic_term_id": setup["term"]["id"],
        },
    )
    assert res.status_code == 404
    assert "Subject not found" in res.json()["detail"]

    # Missing section
    res = client.post(
        "/api/student-enrollments",
        json={
            "student_id": setup["student"]["id"],
            "subject_id": setup["subject"]["id"],
            "section_id": 9999,
            "academic_term_id": setup["term"]["id"],
        },
    )
    assert res.status_code == 404
    assert "Section not found" in res.json()["detail"]

    # Missing academic term
    res = client.post(
        "/api/student-enrollments",
        json={
            "student_id": setup["student"]["id"],
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
    setup = _setup_enrollment_dependencies(client, db_session)

    # Inactive student
    inactive_user = _create_user(
        db_session,
        username="inactive_stu_user",
        email="inactive_stu_user@example.com",
        role="STUDENT",
    )
    inactive_student = client.post(
        "/api/students",
        json={
            "user_id": inactive_user.id,
            "department_id": setup["department"]["id"],
            "section_id": setup["section"]["id"],
            "student_identifier": "STU_INACT_88",
            "enrollment_number": "ENR_INACT_88",
            "first_name": "Inactive",
            "last_name": "Student",
            "admission_year": 2024,
            "is_active": False,
        },
    ).json()

    res = client.post(
        "/api/student-enrollments",
        json={
            "student_id": inactive_student["id"],
            "subject_id": setup["subject"]["id"],
            "section_id": setup["section"]["id"],
            "academic_term_id": setup["term"]["id"],
        },
    )
    assert res.status_code == 400
    assert "Student is not active" in res.json()["detail"]

    # Inactive subject
    inactive_subject = client.post(
        "/api/subjects",
        json={
            "department_id": setup["department"]["id"],
            "subject_code": "CS999INACT",
            "name": "Inactive Subject",
            "credits": 3,
            "is_active": False,
        },
    ).json()

    res = client.post(
        "/api/student-enrollments",
        json={
            "student_id": setup["student"]["id"],
            "subject_id": inactive_subject["id"],
            "section_id": setup["section"]["id"],
            "academic_term_id": setup["term"]["id"],
        },
    )
    assert res.status_code == 400
    assert "Subject is not active" in res.json()["detail"]

    # Inactive academic term
    inactive_term = client.post(
        "/api/academic-terms",
        json={
            "academic_year": "2027",
            "semester": "6",
            "name": "Even Semester 2027 Inactive",
            "start_date": "2027-01-01",
            "end_date": "2027-05-31",
            "is_active": False,
        },
    ).json()

    inactive_term_section = client.post(
        "/api/sections",
        json={
            "program_id": setup["program"]["id"],
            "academic_term_id": inactive_term["id"],
            "name": "B-Inact",
        },
    ).json()

    res = client.post(
        "/api/student-enrollments",
        json={
            "student_id": setup["student"]["id"],
            "subject_id": setup["subject"]["id"],
            "section_id": inactive_term_section["id"],
            "academic_term_id": inactive_term["id"],
        },
    )
    assert res.status_code == 400
    assert "Academic term is not active" in res.json()["detail"]

    # Section mismatch with academic term
    other_active_term = client.post(
        "/api/academic-terms",
        json={
            "academic_year": "2026",
            "semester": "6",
            "name": "Even Semester 2026 Active",
            "start_date": "2026-01-01",
            "end_date": "2026-05-31",
            "is_active": True,
        },
    ).json()

    res = client.post(
        "/api/student-enrollments",
        json={
            "student_id": setup["student"]["id"],
            "subject_id": setup["subject"]["id"],
            "section_id": setup["section"]["id"],
            "academic_term_id": other_active_term["id"],
        },
    )
    assert res.status_code == 400
    assert "Section does not belong to the selected academic term" in res.json()["detail"]

    # Student section mismatch with enrollment section
    other_section_in_same_term = client.post(
        "/api/sections",
        json={
            "program_id": setup["program"]["id"],
            "academic_term_id": setup["term"]["id"],
            "name": "Sec-Diff",
        },
    ).json()

    res = client.post(
        "/api/student-enrollments",
        json={
            "student_id": setup["student"]["id"],
            "subject_id": setup["subject"]["id"],
            "section_id": other_section_in_same_term["id"],
            "academic_term_id": setup["term"]["id"],
        },
    )
    assert res.status_code == 400
    assert "Student's section is not compatible with the enrollment section" in res.json()["detail"]


def test_authorization_and_authentication(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    # Perform setup first while current user is ADMIN
    setup = _setup_enrollment_dependencies(client, db_session)
    payload = {
        "student_id": setup["student"]["id"],
        "subject_id": setup["subject"]["id"],
        "section_id": setup["section"]["id"],
        "academic_term_id": setup["term"]["id"],
    }

    # Faculty can list, but cannot create or delete
    current_user_payload["role"] = "FACULTY"
    listed = client.get("/api/student-enrollments")
    assert listed.status_code == 200

    forbidden_create = client.post("/api/student-enrollments", json=payload)
    assert forbidden_create.status_code == 403

    forbidden_delete = client.delete(f"/api/student-enrollments/{setup['student']['id']}")
    assert forbidden_delete.status_code == 403

    # Student cannot create or list
    current_user_payload["role"] = "STUDENT"
    forbidden_list = client.get("/api/student-enrollments")
    assert forbidden_list.status_code == 403

    forbidden_create_student = client.post("/api/student-enrollments", json=payload)
    assert forbidden_create_student.status_code == 403


def test_anonymous_cannot_list_enrollments(anonymous_client: TestClient):
    anon_response = anonymous_client.get("/api/student-enrollments")
    assert anon_response.status_code in (401, 403)
