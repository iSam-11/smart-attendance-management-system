from __future__ import annotations

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


def _setup_correction_dependencies(
    client: TestClient,
    db_session: Session,
    suffix: str | None = None,
) -> dict:
    if suffix is None:
        suffix = uuid.uuid4().hex[:6]

    code = f"CR{suffix[:4]}".upper()
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
            "name": "Database Management",
            "credits": 4,
            "is_active": True,
        },
    ).json()

    fac_user_1 = _create_user(
        db_session,
        username=f"fac1_{suffix}",
        email=f"fac1_{suffix}@example.com",
        role="FACULTY",
    )
    fac1 = client.post(
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
        username=f"fac2_{suffix}",
        email=f"fac2_{suffix}@example.com",
        role="FACULTY",
    )
    fac2 = client.post(
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
            "faculty_id": fac1["id"],
            "subject_id": subject["id"],
            "section_id": section["id"],
            "academic_term_id": term["id"],
        },
    ).json()

    session_1 = client.post(
        "/api/attendance-sessions",
        json={
            "faculty_assignment_id": assignment_1["id"],
            "session_date": "2026-09-25",
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "topic": "SQL Queries",
        },
    ).json()

    stu_user_1 = _create_user(
        db_session,
        username=f"stu1_{suffix}",
        email=f"stu1_{suffix}@example.com",
        role="STUDENT",
    )
    stu1 = client.post(
        "/api/students",
        json={
            "user_id": stu_user_1.id,
            "department_id": dept["id"],
            "section_id": section["id"],
            "student_identifier": f"S1_{suffix}".upper(),
            "enrollment_number": f"EN1_{suffix}".upper(),
            "first_name": "Student",
            "last_name": "One",
            "admission_year": 2024,
            "is_active": True,
        },
    ).json()
    client.post(
        "/api/student-enrollments",
        json={
            "student_id": stu1["id"],
            "subject_id": subject["id"],
            "section_id": section["id"],
            "academic_term_id": term["id"],
        },
    )

    stu_user_2 = _create_user(
        db_session,
        username=f"stu2_{suffix}",
        email=f"stu2_{suffix}@example.com",
        role="STUDENT",
    )
    stu2 = client.post(
        "/api/students",
        json={
            "user_id": stu_user_2.id,
            "department_id": dept["id"],
            "section_id": section["id"],
            "student_identifier": f"S2_{suffix}".upper(),
            "enrollment_number": f"EN2_{suffix}".upper(),
            "first_name": "Student",
            "last_name": "Two",
            "admission_year": 2024,
            "is_active": True,
        },
    ).json()
    client.post(
        "/api/student-enrollments",
        json={
            "student_id": stu2["id"],
            "subject_id": subject["id"],
            "section_id": section["id"],
            "academic_term_id": term["id"],
        },
    )

    # Attendance: Stu 1 is ABSENT, Stu 2 is ABSENT
    att_res = client.post(
        "/api/student-attendance",
        json={
            "attendance_session_id": session_1["id"],
            "entries": [
                {"student_id": stu1["id"], "status": "ABSENT", "remarks": "Marked absent"},
                {"student_id": stu2["id"], "status": "ABSENT", "remarks": "Marked absent"},
            ],
        },
    )
    attendance_records = att_res.json()
    att_stu1 = attendance_records[0]
    att_stu2 = attendance_records[1]

    return {
        "dept": dept,
        "term": term,
        "section": section,
        "subject": subject,
        "fac_user_1": fac_user_1,
        "fac1": fac1,
        "fac_user_2": fac_user_2,
        "fac2": fac2,
        "assignment_1": assignment_1,
        "session_1": session_1,
        "stu_user_1": stu_user_1,
        "stu1": stu1,
        "stu_user_2": stu_user_2,
        "stu2": stu2,
        "att_stu1": att_stu1,
        "att_stu2": att_stu2,
    }


def test_student_creates_valid_correction_request(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_correction_dependencies(client, db_session)

    current_user_payload["role"] = "STUDENT"
    current_user_payload["sub"] = str(setup["stu_user_1"].id)

    payload = {
        "student_attendance_id": setup["att_stu1"]["id"],
        "requested_status": "PRESENT",
        "reason": "I was present but marked absent by mistake.",
    }

    res = client.post("/api/correction-requests", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["student_attendance_id"] == setup["att_stu1"]["id"]
    assert data["requested_by"] == setup["stu_user_1"].id
    assert data["requested_status"] == "PRESENT"
    assert data["request_status"] == "PENDING"
    assert data["reason"] == "I was present but marked absent by mistake."


def test_student_cannot_request_correction_for_another_student(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_correction_dependencies(client, db_session)

    # Student 1 trying to request correction for Student 2's attendance
    current_user_payload["role"] = "STUDENT"
    current_user_payload["sub"] = str(setup["stu_user_1"].id)

    payload = {
        "student_attendance_id": setup["att_stu2"]["id"],
        "requested_status": "PRESENT",
        "reason": "Trying to fix my friend's attendance",
    }

    res = client.post("/api/correction-requests", json=payload)
    assert res.status_code == 403
    assert "another student" in res.json()["detail"].lower()


def test_missing_attendance_record(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_correction_dependencies(client, db_session)

    current_user_payload["role"] = "STUDENT"
    current_user_payload["sub"] = str(setup["stu_user_1"].id)

    payload = {
        "student_attendance_id": 99999,
        "requested_status": "PRESENT",
        "reason": "Invalid attendance ID",
    }

    res = client.post("/api/correction-requests", json=payload)
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_empty_or_invalid_reason(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_correction_dependencies(client, db_session)

    current_user_payload["role"] = "STUDENT"
    current_user_payload["sub"] = str(setup["stu_user_1"].id)

    payload = {
        "student_attendance_id": setup["att_stu1"]["id"],
        "requested_status": "PRESENT",
        "reason": "   ",  # Whitespace only
    }

    res = client.post("/api/correction-requests", json=payload)
    assert res.status_code == 400
    assert "reason must not be empty" in res.json()["detail"].lower()


def test_invalid_requested_status(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_correction_dependencies(client, db_session)

    current_user_payload["role"] = "STUDENT"
    current_user_payload["sub"] = str(setup["stu_user_1"].id)

    payload = {
        "student_attendance_id": setup["att_stu1"]["id"],
        "requested_status": "EXCUSED",
        "reason": "I had a valid leave letter.",
    }

    res = client.post("/api/correction-requests", json=payload)
    assert res.status_code == 400
    assert "allowed values are present and absent" in res.json()["detail"].lower()


def test_anonymous_access_denied(
    anonymous_client: TestClient,
):
    res_post = anonymous_client.post("/api/correction-requests", json={})
    assert res_post.status_code in (401, 403)

    res_get = anonymous_client.get("/api/correction-requests")
    assert res_get.status_code in (401, 403)


def test_student_access_restrictions(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_correction_dependencies(client, db_session)

    # Student 1 creates a request
    current_user_payload["role"] = "STUDENT"
    current_user_payload["sub"] = str(setup["stu_user_1"].id)
    req1 = client.post(
        "/api/correction-requests",
        json={
            "student_attendance_id": setup["att_stu1"]["id"],
            "requested_status": "PRESENT",
            "reason": "Was present",
        },
    ).json()

    # Student 1 lists requests: sees only their own request
    list_res = client.get("/api/correction-requests")
    assert list_res.status_code == 200
    assert list_res.json()["total"] == 1
    assert list_res.json()["items"][0]["id"] == req1["id"]

    # Student 2 cannot get Student 1's request by ID
    current_user_payload["sub"] = str(setup["stu_user_2"].id)
    get_res_forb = client.get(f"/api/correction-requests/{req1['id']}")
    assert get_res_forb.status_code == 403

    # Student 2 cannot review Student 1's request
    rev_res = client.post(
        f"/api/correction-requests/{req1['id']}/review",
        json={"status": "APPROVED"},
    )
    assert rev_res.status_code == 403


def test_faculty_authorization_and_review(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_correction_dependencies(client, db_session)

    # Student 1 creates a request
    current_user_payload["role"] = "STUDENT"
    current_user_payload["sub"] = str(setup["stu_user_1"].id)
    req = client.post(
        "/api/correction-requests",
        json={
            "student_attendance_id": setup["att_stu1"]["id"],
            "requested_status": "PRESENT",
            "reason": "Attended full class",
        },
    ).json()

    # Faculty 1 (assigned to session) lists requests: sees the request
    current_user_payload["role"] = "FACULTY"
    current_user_payload["sub"] = str(setup["fac_user_1"].id)

    fac1_list = client.get("/api/correction-requests")
    assert fac1_list.status_code == 200
    assert fac1_list.json()["total"] == 1

    # Faculty 2 (unassigned) lists requests: sees 0 requests
    current_user_payload["sub"] = str(setup["fac_user_2"].id)
    fac2_list = client.get("/api/correction-requests")
    assert fac2_list.status_code == 200
    assert fac2_list.json()["total"] == 0

    # Faculty 2 cannot review Faculty 1's class request
    fac2_rev = client.post(
        f"/api/correction-requests/{req['id']}/review",
        json={"status": "APPROVED", "reviewer_remarks": "Not authorized"},
    )
    assert fac2_rev.status_code == 403


def test_approve_request_updates_attendance(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_correction_dependencies(client, db_session)

    # Student 1 creates correction request from ABSENT -> PRESENT
    current_user_payload["role"] = "STUDENT"
    current_user_payload["sub"] = str(setup["stu_user_1"].id)
    req = client.post(
        "/api/correction-requests",
        json={
            "student_attendance_id": setup["att_stu1"]["id"],
            "requested_status": "PRESENT",
            "reason": "Was present in second half of lab.",
        },
    ).json()

    # Verify initial attendance status is ABSENT
    att_before = client.get(
        "/api/student-attendance",
        params={"student_id": setup["stu1"]["id"]},
    ).json()["items"][0]
    assert att_before["status"] == "ABSENT"

    # Faculty 1 approves request
    current_user_payload["role"] = "FACULTY"
    current_user_payload["sub"] = str(setup["fac_user_1"].id)

    rev_res = client.post(
        f"/api/correction-requests/{req['id']}/review",
        json={"status": "APPROVED", "reviewer_remarks": "Verified with attendance sheet"},
    )
    assert rev_res.status_code == 200
    rev_data = rev_res.json()
    assert rev_data["request_status"] == "APPROVED"
    assert rev_data["reviewed_by"] == setup["fac_user_1"].id
    assert rev_data["reviewer_remarks"] == "Verified with attendance sheet"

    # Verify attendance record is NOW updated to PRESENT
    att_after = client.get(
        "/api/student-attendance",
        params={"student_id": setup["stu1"]["id"]},
    ).json()["items"][0]
    assert att_after["status"] == "PRESENT"


def test_reject_request_leaves_attendance_unchanged(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_correction_dependencies(client, db_session)

    # Student 2 creates correction request
    current_user_payload["role"] = "STUDENT"
    current_user_payload["sub"] = str(setup["stu_user_2"].id)
    req = client.post(
        "/api/correction-requests",
        json={
            "student_attendance_id": setup["att_stu2"]["id"],
            "requested_status": "PRESENT",
            "reason": "I think I was present",
        },
    ).json()

    # Admin rejects request
    current_user_payload["role"] = "ADMIN"
    current_user_payload["sub"] = "1"

    rev_res = client.post(
        f"/api/correction-requests/{req['id']}/review",
        json={"status": "REJECTED", "reviewer_remarks": "No evidence of attendance"},
    )
    assert rev_res.status_code == 200
    assert rev_res.json()["request_status"] == "REJECTED"

    # Verify attendance record remains ABSENT
    att_after = client.get(
        "/api/student-attendance",
        params={"student_id": setup["stu2"]["id"]},
    ).json()["items"][0]
    assert att_after["status"] == "ABSENT"


def test_cannot_review_already_reviewed_request(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_correction_dependencies(client, db_session)

    current_user_payload["role"] = "STUDENT"
    current_user_payload["sub"] = str(setup["stu_user_1"].id)
    req = client.post(
        "/api/correction-requests",
        json={
            "student_attendance_id": setup["att_stu1"]["id"],
            "requested_status": "PRESENT",
            "reason": "Late entry",
        },
    ).json()

    current_user_payload["role"] = "ADMIN"
    # First review succeeds
    rev1 = client.post(
        f"/api/correction-requests/{req['id']}/review",
        json={"status": "APPROVED"},
    )
    assert rev1.status_code == 200

    # Second review fails
    rev2 = client.post(
        f"/api/correction-requests/{req['id']}/review",
        json={"status": "REJECTED"},
    )
    assert rev2.status_code == 400
    assert "only pending requests can be reviewed" in rev2.json()["detail"].lower()
