from __future__ import annotations

import uuid
from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.db.models.audit_log import AuditLog
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


def _setup_audit_dependencies(
    client: TestClient,
    db_session: Session,
    suffix: str | None = None,
) -> dict:
    if suffix is None:
        suffix = uuid.uuid4().hex[:6]

    code = f"AL{suffix[:4]}".upper()
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

    sec = client.post(
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
            "name": "Audit Test Subject",
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
            "employee_identifier": f"E1_{suffix}".upper(),
            "first_name": "Faculty",
            "last_name": "Audit",
            "is_active": True,
        },
    ).json()

    assignment_1 = client.post(
        "/api/faculty-assignments",
        json={
            "faculty_id": fac1["id"],
            "subject_id": subject["id"],
            "section_id": sec["id"],
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
            "topic": "Audit Topic",
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
            "section_id": sec["id"],
            "student_identifier": f"S1_{suffix}".upper(),
            "enrollment_number": f"EN1_{suffix}".upper(),
            "first_name": "Student",
            "last_name": "Audit",
            "admission_year": 2024,
            "is_active": True,
        },
    ).json()
    client.post(
        "/api/student-enrollments",
        json={
            "student_id": stu1["id"],
            "subject_id": subject["id"],
            "section_id": sec["id"],
            "academic_term_id": term["id"],
        },
    )

    return {
        "dept": dept,
        "term": term,
        "sec": sec,
        "subject": subject,
        "fac_user_1": fac_user_1,
        "fac1": fac1,
        "assignment_1": assignment_1,
        "session_1": session_1,
        "stu_user_1": stu_user_1,
        "stu1": stu1,
    }


def test_audit_logs_workflow_and_actions(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_audit_dependencies(client, db_session)

    # 1. Faculty 1 marks attendance -> ATTENDANCE_MARKED
    current_user_payload["role"] = "FACULTY"
    current_user_payload["sub"] = str(setup["fac_user_1"].id)

    att_res = client.post(
        "/api/student-attendance",
        json={
            "attendance_session_id": setup["session_1"]["id"],
            "entries": [{"student_id": setup["stu1"]["id"], "status": "ABSENT"}],
        },
    )
    assert att_res.status_code == 201
    att_id = att_res.json()[0]["id"]

    # 2. Student 1 requests correction -> CORRECTION_REQUESTED
    current_user_payload["role"] = "STUDENT"
    current_user_payload["sub"] = str(setup["stu_user_1"].id)

    req_res = client.post(
        "/api/correction-requests",
        json={
            "student_attendance_id": att_id,
            "requested_status": "PRESENT",
            "reason": "I was present.",
        },
    )
    assert req_res.status_code == 201
    req_id = req_res.json()["id"]

    # 3. Faculty 1 approves correction -> CORRECTION_APPROVED
    current_user_payload["role"] = "FACULTY"
    current_user_payload["sub"] = str(setup["fac_user_1"].id)

    app_res = client.post(
        f"/api/correction-requests/{req_id}/review",
        json={"status": "APPROVED", "reviewer_remarks": "Approved after verification"},
    )
    assert app_res.status_code == 200

    # 4. Admin inspects audit logs
    current_user_payload["role"] = "ADMIN"
    current_user_payload["sub"] = "1"

    logs_res = client.get("/api/audit-logs")
    assert logs_res.status_code == 200
    logs_data = logs_res.json()
    assert logs_data["total"] >= 3

    actions = [item["action"] for item in logs_data["items"]]
    assert "ATTENDANCE_MARKED" in actions
    assert "CORRECTION_REQUESTED" in actions
    assert "CORRECTION_APPROVED" in actions

    att_marked_log = next(i for i in logs_data["items"] if i["action"] == "ATTENDANCE_MARKED")
    assert att_marked_log["entity_type"] == "AttendanceSession"
    assert att_marked_log["entity_id"] == setup["session_1"]["id"]


def test_correction_rejection_audit_log(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_audit_dependencies(client, db_session)

    current_user_payload["role"] = "FACULTY"
    current_user_payload["sub"] = str(setup["fac_user_1"].id)
    att_id = client.post(
        "/api/student-attendance",
        json={
            "attendance_session_id": setup["session_1"]["id"],
            "entries": [{"student_id": setup["stu1"]["id"], "status": "ABSENT"}],
        },
    ).json()[0]["id"]

    current_user_payload["role"] = "STUDENT"
    current_user_payload["sub"] = str(setup["stu_user_1"].id)
    req_id = client.post(
        "/api/correction-requests",
        json={
            "student_attendance_id": att_id,
            "requested_status": "PRESENT",
            "reason": "Was present",
        },
    ).json()["id"]

    current_user_payload["role"] = "ADMIN"
    client.post(
        f"/api/correction-requests/{req_id}/review",
        json={"status": "REJECTED", "reviewer_remarks": "Rejected"},
    )

    logs = client.get("/api/audit-logs", params={"action": "CORRECTION_REJECTED"}).json()
    assert logs["total"] == 1
    assert logs["items"][0]["action"] == "CORRECTION_REJECTED"


def test_audit_logs_authorization_and_filters(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_audit_dependencies(client, db_session)

    # Faculty 1 marks attendance
    current_user_payload["role"] = "FACULTY"
    current_user_payload["sub"] = str(setup["fac_user_1"].id)
    client.post(
        "/api/student-attendance",
        json={
            "attendance_session_id": setup["session_1"]["id"],
            "entries": [{"student_id": setup["stu1"]["id"], "status": "PRESENT"}],
        },
    )

    # Student cannot view audit logs
    current_user_payload["role"] = "STUDENT"
    current_user_payload["sub"] = str(setup["stu_user_1"].id)
    stu_res = client.get("/api/audit-logs")
    assert stu_res.status_code == 403

    # Faculty 1 can view their own audit logs
    current_user_payload["role"] = "FACULTY"
    current_user_payload["sub"] = str(setup["fac_user_1"].id)
    fac_res = client.get("/api/audit-logs")
    assert fac_res.status_code == 200
    assert fac_res.json()["total"] >= 1

    # Faculty 1 querying user_id of another user -> 403
    fac_forb = client.get("/api/audit-logs", params={"user_id": 999})
    assert fac_forb.status_code == 403

    # Admin can filter by user_id, action, date range, pagination
    current_user_payload["role"] = "ADMIN"
    admin_res = client.get(
        "/api/audit-logs",
        params={
            "user_id": setup["fac_user_1"].id,
            "action": "ATTENDANCE_MARKED",
            "page": 1,
            "page_size": 10,
        },
    )
    assert admin_res.status_code == 200
    assert admin_res.json()["total"] >= 1


def test_anonymous_cannot_access_audit_logs(
    anonymous_client: TestClient,
):
    res = anonymous_client.get("/api/audit-logs")
    assert res.status_code in (401, 403)


def test_attendance_session_creation_generates_audit_log(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_audit_dependencies(client, db_session)

    # Act as FACULTY and create a NEW attendance session via POST /api/attendance-sessions
    current_user_payload["role"] = "FACULTY"
    current_user_payload["sub"] = str(setup["fac_user_1"].id)

    res = client.post(
        "/api/attendance-sessions",
        json={
            "faculty_assignment_id": setup["assignment_1"]["id"],
            "session_date": "2026-09-26",
            "start_time": "11:00:00",
            "end_time": "12:00:00",
            "topic": "Live Audit Test Session",
        },
    )
    assert res.status_code == 201
    session_id = res.json()["id"]

    # Verify directly in DB that AuditLog record exists
    audit_record = (
        db_session.query(AuditLog)
        .filter(
            AuditLog.entity_type == "AttendanceSession",
            AuditLog.entity_id == session_id,
            AuditLog.action == "SESSION_CREATED",
        )
        .first()
    )
    assert audit_record is not None
    assert audit_record.user_id == setup["fac_user_1"].id

    # Also verify through GET /api/audit-logs endpoint as ADMIN
    current_user_payload["role"] = "ADMIN"
    current_user_payload["sub"] = "1"
    audit_res = client.get("/api/audit-logs", params={"action": "SESSION_CREATED"})
    assert audit_res.status_code == 200
    items = audit_res.json()["items"]
    matching = [i for i in items if i["entity_id"] == session_id]
    assert len(matching) == 1
    assert matching[0]["action"] == "SESSION_CREATED"
    assert matching[0]["user_id"] == setup["fac_user_1"].id

