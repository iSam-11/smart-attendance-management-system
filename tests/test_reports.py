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


def _setup_report_dependencies(
    client: TestClient,
    db_session: Session,
    suffix: str | None = None,
) -> dict:
    if suffix is None:
        suffix = uuid.uuid4().hex[:6]

    code = f"RP{suffix[:4]}".upper()
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

    sec1 = client.post(
        "/api/sections",
        json={
            "program_id": program["id"],
            "academic_term_id": term["id"],
            "name": f"Sec1-{suffix}",
        },
    ).json()

    sec2 = client.post(
        "/api/sections",
        json={
            "program_id": program["id"],
            "academic_term_id": term["id"],
            "name": f"Sec2-{suffix}",
        },
    ).json()

    subj1 = client.post(
        "/api/subjects",
        json={
            "department_id": dept["id"],
            "subject_code": f"SUB1-{suffix}".upper(),
            "name": "Data Structures",
            "credits": 4,
            "is_active": True,
        },
    ).json()

    subj2 = client.post(
        "/api/subjects",
        json={
            "department_id": dept["id"],
            "subject_code": f"SUB2-{suffix}".upper(),
            "name": "Computer Networks",
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
            "department_id": dept["id"],
            "employee_identifier": f"E2_{suffix}".upper(),
            "first_name": "Prof",
            "last_name": "Two",
            "is_active": True,
        },
    ).json()

    # Assignment 1: Faculty 1 -> Subj 1, Sec 1, Term
    assign1 = client.post(
        "/api/faculty-assignments",
        json={
            "faculty_id": fac1["id"],
            "subject_id": subj1["id"],
            "section_id": sec1["id"],
            "academic_term_id": term["id"],
        },
    ).json()

    # Assignment 2: Faculty 2 -> Subj 2, Sec 2, Term
    assign2 = client.post(
        "/api/faculty-assignments",
        json={
            "faculty_id": fac2["id"],
            "subject_id": subj2["id"],
            "section_id": sec2["id"],
            "academic_term_id": term["id"],
        },
    ).json()

    # Students setup
    stu_user_1 = _create_user(
        db_session, username=f"stu1_{suffix}", email=f"stu1_{suffix}@example.com", role="STUDENT"
    )
    stu1 = client.post(
        "/api/students",
        json={
            "user_id": stu_user_1.id,
            "department_id": dept["id"],
            "section_id": sec1["id"],
            "student_identifier": f"S1_{suffix}".upper(),
            "enrollment_number": f"EN1_{suffix}".upper(),
            "first_name": "Student",
            "last_name": "FiftyPercent",
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
            "academic_term_id": term["id"],
        },
    )

    stu_user_2 = _create_user(
        db_session, username=f"stu2_{suffix}", email=f"stu2_{suffix}@example.com", role="STUDENT"
    )
    stu2 = client.post(
        "/api/students",
        json={
            "user_id": stu_user_2.id,
            "department_id": dept["id"],
            "section_id": sec1["id"],
            "student_identifier": f"S2_{suffix}".upper(),
            "enrollment_number": f"EN2_{suffix}".upper(),
            "first_name": "Student",
            "last_name": "SeventyFivePercent",
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
            "academic_term_id": term["id"],
        },
    )

    stu_user_3 = _create_user(
        db_session, username=f"stu3_{suffix}", email=f"stu3_{suffix}@example.com", role="STUDENT"
    )
    stu3 = client.post(
        "/api/students",
        json={
            "user_id": stu_user_3.id,
            "department_id": dept["id"],
            "section_id": sec1["id"],
            "student_identifier": f"S3_{suffix}".upper(),
            "enrollment_number": f"EN3_{suffix}".upper(),
            "first_name": "Student",
            "last_name": "HundredPercent",
            "admission_year": 2024,
            "is_active": True,
        },
    ).json()
    client.post(
        "/api/student-enrollments",
        json={
            "student_id": stu3["id"],
            "subject_id": subj1["id"],
            "section_id": sec1["id"],
            "academic_term_id": term["id"],
        },
    )

    stu_user_4 = _create_user(
        db_session, username=f"stu4_{suffix}", email=f"stu4_{suffix}@example.com", role="STUDENT"
    )
    stu4 = client.post(
        "/api/students",
        json={
            "user_id": stu_user_4.id,
            "department_id": dept["id"],
            "section_id": sec2["id"],
            "student_identifier": f"S4_{suffix}".upper(),
            "enrollment_number": f"EN4_{suffix}".upper(),
            "first_name": "Student",
            "last_name": "ZeroConducted",
            "admission_year": 2024,
            "is_active": True,
        },
    ).json()
    client.post(
        "/api/student-enrollments",
        json={
            "student_id": stu4["id"],
            "subject_id": subj2["id"],
            "section_id": sec2["id"],
            "academic_term_id": term["id"],
        },
    )

    # Sessions & Attendance for Subj 1 (Sec 1)
    # Conduct 4 sessions:
    # Sess 1: 2026-09-01
    # Sess 2: 2026-09-02
    # Sess 3: 2026-09-03
    # Sess 4: 2026-09-04
    dates = ["2026-09-01", "2026-09-02", "2026-09-03", "2026-09-04"]
    sessions = []
    for d in dates:
        s = client.post(
            "/api/attendance-sessions",
            json={
                "faculty_assignment_id": assign1["id"],
                "session_date": d,
                "start_time": "09:00:00",
            },
        ).json()
        sessions.append(s)

    # Stu 1: Present in 2/4 sessions (50.0%)
    # Stu 2: Present in 3/4 sessions (75.0%)
    # Stu 3: Present in 4/4 sessions (100.0%)
    stu1_status = ["PRESENT", "PRESENT", "ABSENT", "ABSENT"]
    stu2_status = ["PRESENT", "PRESENT", "PRESENT", "ABSENT"]
    stu3_status = ["PRESENT", "PRESENT", "PRESENT", "PRESENT"]

    for idx, sess in enumerate(sessions):
        client.post(
            "/api/student-attendance",
            json={
                "attendance_session_id": sess["id"],
                "entries": [
                    {"student_id": stu1["id"], "status": stu1_status[idx]},
                    {"student_id": stu2["id"], "status": stu2_status[idx]},
                    {"student_id": stu3["id"], "status": stu3_status[idx]},
                ],
            },
        )

    return {
        "dept": dept,
        "term": term,
        "sec1": sec1,
        "sec2": sec2,
        "subj1": subj1,
        "subj2": subj2,
        "fac_user_1": fac_user_1,
        "fac1": fac1,
        "fac_user_2": fac_user_2,
        "fac2": fac2,
        "assign1": assign1,
        "assign2": assign2,
        "stu_user_1": stu_user_1,
        "stu1": stu1,
        "stu_user_2": stu_user_2,
        "stu2": stu2,
        "stu_user_3": stu_user_3,
        "stu3": stu3,
        "stu_user_4": stu_user_4,
        "stu4": stu4,
        "sessions": sessions,
    }


def test_admin_can_access_all_reports(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    current_user_payload["role"] = "ADMIN"
    setup = _setup_report_dependencies(client, db_session)

    r_student = client.get("/api/reports/student-attendance")
    assert r_student.status_code == 200

    r_subject = client.get("/api/reports/subject-attendance")
    assert r_subject.status_code == 200

    r_section = client.get("/api/reports/section-attendance")
    assert r_section.status_code == 200

    r_low = client.get("/api/reports/low-attendance")
    assert r_low.status_code == 200


def test_faculty_can_access_assigned_class_reports(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_report_dependencies(client, db_session)

    current_user_payload["role"] = "FACULTY"
    current_user_payload["sub"] = str(setup["fac_user_1"].id)

    res = client.get(
        "/api/reports/subject-attendance",
        params={"subject_id": setup["subj1"]["id"]},
    )
    assert res.status_code == 200
    assert res.json()["total"] == 3


def test_faculty_cannot_access_unassigned_class_reports(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_report_dependencies(client, db_session)

    # Faculty 2 tries to access Subject 1 report (assigned to Faculty 1)
    current_user_payload["role"] = "FACULTY"
    current_user_payload["sub"] = str(setup["fac_user_2"].id)

    res = client.get(
        "/api/reports/subject-attendance",
        params={"subject_id": setup["subj1"]["id"]},
    )
    assert res.status_code == 403
    assert "only for assigned subjects" in res.json()["detail"].lower()


def test_student_can_access_own_attendance_report(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_report_dependencies(client, db_session)

    current_user_payload["role"] = "STUDENT"
    current_user_payload["sub"] = str(setup["stu_user_1"].id)

    res = client.get("/api/reports/student-attendance")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    item = data["items"][0]
    assert item["student_id"] == setup["stu1"]["id"]
    assert item["total_conducted_classes"] == 4
    assert item["present_classes"] == 2
    assert item["attendance_percentage"] == 50.0


def test_student_cannot_access_another_student_report_or_class_reports(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    setup = _setup_report_dependencies(client, db_session)

    current_user_payload["role"] = "STUDENT"
    current_user_payload["sub"] = str(setup["stu_user_1"].id)

    # Student 1 querying Student 2's report
    res_other = client.get(
        "/api/reports/student-attendance",
        params={"student_id": setup["stu2"]["id"]},
    )
    assert res_other.status_code == 403

    # Student 1 querying Subject / Section / Low attendance reports
    assert client.get("/api/reports/subject-attendance").status_code == 403
    assert client.get("/api/reports/section-attendance").status_code == 403
    assert client.get("/api/reports/low-attendance").status_code == 403


def test_anonymous_access_returns_401(
    anonymous_client: TestClient,
):
    assert anonymous_client.get("/api/reports/student-attendance").status_code in (401, 403)
    assert anonymous_client.get("/api/reports/subject-attendance").status_code in (401, 403)
    assert anonymous_client.get("/api/reports/section-attendance").status_code in (401, 403)
    assert anonymous_client.get("/api/reports/low-attendance").status_code in (401, 403)


def test_student_attendance_calculation(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    current_user_payload["role"] = "ADMIN"
    setup = _setup_report_dependencies(client, db_session)

    res = client.get(
        "/api/reports/student-attendance",
        params={"student_id": setup["stu1"]["id"]},
    )
    assert res.status_code == 200
    item = res.json()["items"][0]
    assert item["total_conducted_classes"] == 4
    assert item["present_classes"] == 2
    assert item["absent_classes"] == 2
    assert item["attendance_percentage"] == 50.0


def test_subject_attendance_calculation(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    current_user_payload["role"] = "ADMIN"
    setup = _setup_report_dependencies(client, db_session)

    res = client.get(
        "/api/reports/subject-attendance",
        params={"subject_id": setup["subj1"]["id"]},
    )
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) == 3

    # Map percentages by student_id
    pct_map = {item["student_id"]: item["attendance_percentage"] for item in items}
    assert pct_map[setup["stu1"]["id"]] == 50.0
    assert pct_map[setup["stu2"]["id"]] == 75.0
    assert pct_map[setup["stu3"]["id"]] == 100.0


def test_section_attendance_calculation(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    current_user_payload["role"] = "ADMIN"
    setup = _setup_report_dependencies(client, db_session)

    res = client.get(
        "/api/reports/section-attendance",
        params={"section_id": setup["sec1"]["id"]},
    )
    assert res.status_code == 200
    assert res.json()["total"] == 3


def test_low_attendance_threshold_and_boundary(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    current_user_payload["role"] = "ADMIN"
    setup = _setup_report_dependencies(client, db_session)

    # Threshold 75.0%
    # Stu 1 (50.0%) < 75.0 -> Included
    # Stu 2 (75.0%) == 75.0 -> Excluded
    # Stu 3 (100.0%) > 75.0 -> Excluded
    res_75 = client.get(
        "/api/reports/low-attendance",
        params={"threshold": 75.0, "subject_id": setup["subj1"]["id"]},
    )
    assert res_75.status_code == 200
    items_75 = res_75.json()["items"]
    assert len(items_75) == 1
    assert items_75[0]["student_id"] == setup["stu1"]["id"]
    assert items_75[0]["attendance_percentage"] == 50.0
    assert items_75[0]["threshold"] == 75.0

    # Threshold 80.0%
    # Stu 1 (50.0%) and Stu 2 (75.0%) < 80.0 -> Included (2 students)
    res_80 = client.get(
        "/api/reports/low-attendance",
        params={"threshold": 80.0, "subject_id": setup["subj1"]["id"]},
    )
    assert res_80.status_code == 200
    assert res_80.json()["total"] == 2


def test_date_range_filtering(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    current_user_payload["role"] = "ADMIN"
    setup = _setup_report_dependencies(client, db_session)

    # Filter sessions between 2026-09-01 and 2026-09-02 (2 sessions conducted)
    # Stu 1 present in both sessions on 01 and 02 -> 2/2 = 100.0%
    res = client.get(
        "/api/reports/student-attendance",
        params={
            "student_id": setup["stu1"]["id"],
            "start_date": "2026-09-01",
            "end_date": "2026-09-02",
        },
    )
    assert res.status_code == 200
    item = res.json()["items"][0]
    assert item["total_conducted_classes"] == 2
    assert item["present_classes"] == 2
    assert item["attendance_percentage"] == 100.0


def test_zero_conducted_classes_no_division_by_zero(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    current_user_payload["role"] = "ADMIN"
    setup = _setup_report_dependencies(client, db_session)

    # Student 4 is in Section 2, Subject 2 where NO sessions have been conducted
    res = client.get(
        "/api/reports/student-attendance",
        params={"student_id": setup["stu4"]["id"]},
    )
    assert res.status_code == 200
    item = res.json()["items"][0]
    assert item["total_conducted_classes"] == 0
    assert item["present_classes"] == 0
    assert item["attendance_percentage"] == 0.0


def test_pagination_and_empty_result_sets(
    client: TestClient,
    current_user_payload: dict,
    db_session: Session,
):
    current_user_payload["role"] = "ADMIN"
    setup = _setup_report_dependencies(client, db_session)

    # Pagination
    res_p1 = client.get(
        "/api/reports/subject-attendance",
        params={"subject_id": setup["subj1"]["id"], "page": 1, "page_size": 2},
    )
    assert res_p1.status_code == 200
    data_p1 = res_p1.json()
    assert data_p1["page"] == 1
    assert data_p1["page_size"] == 2
    assert data_p1["total"] == 3
    assert len(data_p1["items"]) == 2

    # Empty result set
    res_empty = client.get(
        "/api/reports/subject-attendance",
        params={"subject_id": 99999},
    )
    assert res_empty.status_code == 200
    assert res_empty.json()["total"] == 0
    assert len(res_empty.json()["items"]) == 0
