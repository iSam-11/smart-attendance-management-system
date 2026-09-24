import uuid
from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.db.models.student import Student
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


def _setup_attendance_dependencies(
    client: TestClient,
    db_session: Session,
    suffix: str | None = None,
) -> dict:
    if suffix is None:
        suffix = uuid.uuid4().hex[:6]

    code = f"SA{suffix[:4]}".upper()
    dept1 = client.post(
        "/api/departments",
        json={"name": f"Dept1 {suffix}", "code": code},
    ).json()

    dept2 = client.post(
        "/api/departments",
        json={"name": f"Dept2 {suffix}", "code": f"D2{code}"},
    ).json()

    program1 = client.post(
        "/api/programs",
        json={
            "department_id": dept1["id"],
            "name": f"B.Tech {suffix}",
            "code": f"BT-{code}",
        },
    ).json()

    term1 = client.post(
        "/api/academic-terms",
        json={
            "academic_year": "2026",
            "semester": "5",
            "name": f"Term1 {suffix}",
            "start_date": "2026-07-01",
            "end_date": "2026-12-15",
            "is_active": True,
        },
    ).json()

    term2 = client.post(
        "/api/academic-terms",
        json={
            "academic_year": "2026",
            "semester": "6",
            "name": f"Term2 {suffix}",
            "start_date": "2027-01-01",
            "end_date": "2027-05-31",
            "is_active": True,
        },
    ).json()

    sec1 = client.post(
        "/api/sections",
        json={
            "program_id": program1["id"],
            "academic_term_id": term1["id"],
            "name": f"Sec1-{suffix}",
        },
    ).json()

    sec2 = client.post(
        "/api/sections",
        json={
            "program_id": program1["id"],
            "academic_term_id": term1["id"],
            "name": f"Sec2-{suffix}",
        },
    ).json()

    sec3 = client.post(
        "/api/sections",
        json={
            "program_id": program1["id"],
            "academic_term_id": term2["id"],
            "name": f"Sec3-{suffix}",
        },
    ).json()

    subj1 = client.post(
        "/api/subjects",
        json={
            "department_id": dept1["id"],
            "subject_code": f"SUB1-{suffix}".upper(),
            "name": "Algorithms",
            "credits": 4,
            "is_active": True,
        },
    ).json()

    subj2 = client.post(
        "/api/subjects",
        json={
            "department_id": dept1["id"],
            "subject_code": f"SUB2-{suffix}".upper(),
            "name": "Operating Systems",
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
            "department_id": dept1["id"],
            "employee_identifier": f"E1_{suffix}".upper(),
            "first_name": "Prof",
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
            "department_id": dept1["id"],
            "employee_identifier": f"E2_{suffix}".upper(),
            "first_name": "Prof",
            "last_name": "Two",
            "is_active": True,
        },
    ).json()

    assignment_1 = client.post(
        "/api/faculty-assignments",
        json={
            "faculty_id": fac1["id"],
            "subject_id": subj1["id"],
            "section_id": sec1["id"],
            "academic_term_id": term1["id"],
        },
    ).json()

    session_1 = client.post(
        "/api/attendance-sessions",
        json={
            "faculty_assignment_id": assignment_1["id"],
            "session_date": "2026-09-25",
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "topic": "Algorithms Session 1",
        },
    ).json()

    # Students setup
    # Student 1 & 2: Enrolled in Subj1, Sec1, Term1
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
            "department_id": dept1["id"],
            "section_id": sec1["id"],
            "student_identifier": f"S1_{suffix}".upper(),
            "enrollment_number": f"EN1_{suffix}".upper(),
            "first_name": "Alice",
            "last_name": "Smith",
            "admission_year": 2024,
            "is_active": True,
        },
    ).json()
    client.post(
        "/api/student-enrollments",
        json={
            "student_id": stu1["id"],
            "subject_id": subj1["id"],
            "section_id": sec1["id"],
            "academic_term_id": term1["id"],
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
            "department_id": dept1["id"],
            "section_id": sec1["id"],
            "student_identifier": f"S2_{suffix}".upper(),
            "enrollment_number": f"EN2_{suffix}".upper(),
            "first_name": "Bob",
            "last_name": "Jones",
            "admission_year": 2024,
            "is_active": True,
        },
    ).json()
    client.post(
        "/api/student-enrollments",
        json={
            "student_id": stu2["id"],
            "subject_id": subj1["id"],
            "section_id": sec1["id"],
            "academic_term_id": term1["id"],
        },
    )

    # Student 3: Enrolled in Subj2 (Wrong Subject)
    stu_user_3 = _create_user(
        db_session,
        username=f"stu3_{suffix}",
        email=f"stu3_{suffix}@example.com",
        role="STUDENT",
    )
    stu3 = client.post(
        "/api/students",
        json={
            "user_id": stu_user_3.id,
            "department_id": dept1["id"],
            "section_id": sec1["id"],
            "student_identifier": f"S3_{suffix}".upper(),
            "enrollment_number": f"EN3_{suffix}".upper(),
            "first_name": "Charlie",
            "last_name": "Brown",
            "admission_year": 2024,
            "is_active": True,
        },
    ).json()
    client.post(
        "/api/student-enrollments",
        json={
            "student_id": stu3["id"],
            "subject_id": subj2["id"],
            "section_id": sec1["id"],
            "academic_term_id": term1["id"],
        },
    )

    # Student 4: Enrolled in Sec2 (Wrong Section)
    stu_user_4 = _create_user(
        db_session,
        username=f"stu4_{suffix}",
        email=f"stu4_{suffix}@example.com",
        role="STUDENT",
    )
    stu4 = client.post(
        "/api/students",
        json={
            "user_id": stu_user_4.id,
            "department_id": dept1["id"],
            "section_id": sec2["id"],
            "student_identifier": f"S4_{suffix}".upper(),
            "enrollment_number": f"EN4_{suffix}".upper(),
            "first_name": "David",
            "last_name": "Miller",
            "admission_year": 2024,
            "is_active": True,
        },
    ).json()
    client.post(
        "/api/student-enrollments",
        json={
            "student_id": stu4["id"],
            "subject_id": subj1["id"],
            "section_id": sec2["id"],
            "academic_term_id": term1["id"],
        },
    )

    # Student 5: Enrolled in Term2 (Wrong Term)
    stu_user_5 = _create_user(
        db_session,
        username=f"stu5_{suffix}",
        email=f"stu5_{suffix}@example.com",
        role="STUDENT",
    )
    stu5 = client.post(
        "/api/students",
        json={
            "user_id": stu_user_5.id,
            "department_id": dept1["id"],
            "section_id": sec3["id"],
            "student_identifier": f"S5_{suffix}".upper(),
            "enrollment_number": f"EN5_{suffix}".upper(),
            "first_name": "Eve",
            "last_name": "Davis",
            "admission_year": 2024,
            "is_active": True,
        },
    ).json()
    client.post(
        "/api/student-enrollments",
        json={
            "student_id": stu5["id"],
            "subject_id": subj1["id"],
            "section_id": sec3["id"],
            "academic_term_id": term2["id"],
        },
    )

    # Student 6: Inactive Student enrolled in Subj1, Sec1, Term1
    stu_user_6 = _create_user(
        db_session,
        username=f"stu6_{suffix}",
        email=f"stu6_{suffix}@example.com",
        role="STUDENT",
    )
    stu6 = client.post(
        "/api/students",
        json={
            "user_id": stu_user_6.id,
            "department_id": dept1["id"],
            "section_id": sec1["id"],
            "student_identifier": f"S6_{suffix}".upper(),
            "enrollment_number": f"EN6_{suffix}".upper(),
            "first_name": "Frank",
            "last_name": "Inactive",
            "admission_year": 2024,
            "is_active": False,
        },
    ).json()
    client.post(
        "/api/student-enrollments",
        json={
            "student_id": stu6["id"],
            "subject_id": subj1["id"],
            "section_id": sec1["id"],
            "academic_term_id": term1["id"],
        },
    )

    return {
        "dept1": dept1,
        "term1": term1,
        "sec1": sec1,
        "subj1": subj1,
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
        "stu3": stu3,
        "stu4": stu4,
        "stu5": stu5,
        "stu6": stu6,
    }


def test_bulk_attendance_valid_present_and_absent(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    current_user_payload["role"] = "ADMIN"
    setup = _setup_attendance_dependencies(client, db_session)

    payload = {
        "attendance_session_id": setup["session_1"]["id"],
        "entries": [
            {
                "student_id": setup["stu1"]["id"],
                "status": "PRESENT",
                "remarks": "On time",
            },
            {
                "student_id": setup["stu2"]["id"],
                "status": "ABSENT",
                "remarks": "Illness",
            },
        ],
    }

    res = client.post("/api/student-attendance", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert len(data) == 2
    assert data[0]["student_id"] == setup["stu1"]["id"]
    assert data[0]["status"] == "PRESENT"
    assert data[0]["remarks"] == "On time"
    assert data[1]["student_id"] == setup["stu2"]["id"]
    assert data[1]["status"] == "ABSENT"


def test_only_enrolled_students_can_be_marked(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    current_user_payload["role"] = "ADMIN"
    setup = _setup_attendance_dependencies(client, db_session)

    # Student 3: wrong subject
    res_wrong_subj = client.post(
        "/api/student-attendance",
        json={
            "attendance_session_id": setup["session_1"]["id"],
            "entries": [{"student_id": setup["stu3"]["id"], "status": "PRESENT"}],
        },
    )
    assert res_wrong_subj.status_code == 400
    assert "not enrolled" in res_wrong_subj.json()["detail"].lower()

    # Student 4: wrong section
    res_wrong_sec = client.post(
        "/api/student-attendance",
        json={
            "attendance_session_id": setup["session_1"]["id"],
            "entries": [{"student_id": setup["stu4"]["id"], "status": "PRESENT"}],
        },
    )
    assert res_wrong_sec.status_code == 400
    assert "not enrolled" in res_wrong_sec.json()["detail"].lower()

    # Student 5: wrong academic term
    res_wrong_term = client.post(
        "/api/student-attendance",
        json={
            "attendance_session_id": setup["session_1"]["id"],
            "entries": [{"student_id": setup["stu5"]["id"], "status": "PRESENT"}],
        },
    )
    assert res_wrong_term.status_code == 400
    assert "not enrolled" in res_wrong_term.json()["detail"].lower()


def test_inactive_student_rejected(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    current_user_payload["role"] = "ADMIN"
    setup = _setup_attendance_dependencies(client, db_session)

    res = client.post(
        "/api/student-attendance",
        json={
            "attendance_session_id": setup["session_1"]["id"],
            "entries": [{"student_id": setup["stu6"]["id"], "status": "PRESENT"}],
        },
    )
    assert res.status_code == 400
    assert "not active" in res.json()["detail"].lower()


def test_invalid_status_rejected(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    current_user_payload["role"] = "ADMIN"
    setup = _setup_attendance_dependencies(client, db_session)

    res = client.post(
        "/api/student-attendance",
        json={
            "attendance_session_id": setup["session_1"]["id"],
            "entries": [{"student_id": setup["stu1"]["id"], "status": "LATE"}],
        },
    )
    assert res.status_code == 400
    assert "status must be present or absent" in res.json()["detail"].lower()


def test_duplicate_attendance_rejected(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    current_user_payload["role"] = "ADMIN"
    setup = _setup_attendance_dependencies(client, db_session)

    payload = {
        "attendance_session_id": setup["session_1"]["id"],
        "entries": [{"student_id": setup["stu1"]["id"], "status": "PRESENT"}],
    }

    res1 = client.post("/api/student-attendance", json=payload)
    assert res1.status_code == 201

    # Second submission for same session and student
    res2 = client.post("/api/student-attendance", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"].lower()


def test_faculty_authorization_for_attendance_marking(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_attendance_dependencies(client, db_session)

    # Faculty 1 (assigned faculty) can mark attendance
    current_user_payload["role"] = "FACULTY"
    current_user_payload["sub"] = str(setup["fac_user_1"].id)

    res_fac1 = client.post(
        "/api/student-attendance",
        json={
            "attendance_session_id": setup["session_1"]["id"],
            "entries": [{"student_id": setup["stu1"]["id"], "status": "PRESENT"}],
        },
    )
    assert res_fac1.status_code == 201

    # Faculty 2 (not assigned to session 1) cannot mark attendance
    current_user_payload["sub"] = str(setup["fac_user_2"].id)

    res_fac2 = client.post(
        "/api/student-attendance",
        json={
            "attendance_session_id": setup["session_1"]["id"],
            "entries": [{"student_id": setup["stu2"]["id"], "status": "PRESENT"}],
        },
    )
    assert res_fac2.status_code == 403
    assert "faculty cannot mark attendance" in res_fac2.json()["detail"].lower()


def test_student_cannot_create_attendance(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_attendance_dependencies(client, db_session)

    current_user_payload["role"] = "STUDENT"
    current_user_payload["sub"] = str(setup["stu_user_1"].id)

    res = client.post(
        "/api/student-attendance",
        json={
            "attendance_session_id": setup["session_1"]["id"],
            "entries": [{"student_id": setup["stu1"]["id"], "status": "PRESENT"}],
        },
    )
    assert res.status_code == 403


def test_transactional_bulk_attendance_rollback(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    current_user_payload["role"] = "ADMIN"
    setup = _setup_attendance_dependencies(client, db_session)

    # Payload with student 1 (valid) and student 3 (wrong subject / invalid)
    payload = {
        "attendance_session_id": setup["session_1"]["id"],
        "entries": [
            {"student_id": setup["stu1"]["id"], "status": "PRESENT"},
            {"student_id": setup["stu3"]["id"], "status": "PRESENT"},
        ],
    }

    res = client.post("/api/student-attendance", json=payload)
    assert res.status_code == 400

    # Ensure student 1 was NOT saved (rollback verification)
    history = client.get(
        "/api/student-attendance",
        params={"attendance_session_id": setup["session_1"]["id"]},
    )
    assert history.status_code == 200
    assert history.json()["total"] == 0


def test_attendance_history_and_listing_authorization(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    current_user_payload["role"] = "ADMIN"
    setup = _setup_attendance_dependencies(client, db_session)

    client.post(
        "/api/student-attendance",
        json={
            "attendance_session_id": setup["session_1"]["id"],
            "entries": [
                {"student_id": setup["stu1"]["id"], "status": "PRESENT"},
                {"student_id": setup["stu2"]["id"], "status": "ABSENT"},
            ],
        },
    )

    # Admin access: sees all records
    current_user_payload["role"] = "ADMIN"
    admin_res = client.get("/api/student-attendance")
    assert admin_res.status_code == 200
    assert admin_res.json()["total"] == 2

    # Filter by student_id
    admin_filter = client.get(
        "/api/student-attendance",
        params={"student_id": setup["stu1"]["id"]},
    )
    assert admin_filter.status_code == 200
    assert admin_filter.json()["total"] == 1
    assert admin_filter.json()["items"][0]["student_id"] == setup["stu1"]["id"]

    # Filter by status
    admin_status_filter = client.get(
        "/api/student-attendance",
        params={"status": "ABSENT"},
    )
    assert admin_status_filter.status_code == 200
    assert admin_status_filter.json()["total"] == 1
    assert admin_status_filter.json()["items"][0]["status"] == "ABSENT"

    # Faculty 1 access: sees records for their session
    current_user_payload["role"] = "FACULTY"
    current_user_payload["sub"] = str(setup["fac_user_1"].id)
    fac1_res = client.get("/api/student-attendance")
    assert fac1_res.status_code == 200
    assert fac1_res.json()["total"] == 2

    # Faculty 2 access: sees 0 records
    current_user_payload["sub"] = str(setup["fac_user_2"].id)
    fac2_res = client.get("/api/student-attendance")
    assert fac2_res.status_code == 200
    assert fac2_res.json()["total"] == 0

    # Student 1 access: sees ONLY student 1's record
    current_user_payload["role"] = "STUDENT"
    current_user_payload["sub"] = str(setup["stu_user_1"].id)
    stu1_res = client.get("/api/student-attendance")
    assert stu1_res.status_code == 200
    assert stu1_res.json()["total"] == 1
    assert stu1_res.json()["items"][0]["student_id"] == setup["stu1"]["id"]

    # Student 1 querying Student 2's id is forbidden
    stu1_forb = client.get(
        "/api/student-attendance",
        params={"student_id": setup["stu2"]["id"]},
    )
    assert stu1_forb.status_code == 403
