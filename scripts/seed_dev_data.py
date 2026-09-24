from datetime import date
from sqlalchemy import select

from backend.app.db.session import SessionLocal
from backend.app.db.models.user import User
from backend.app.db.models.department import Department
from backend.app.db.models.academic_term import AcademicTerm
from backend.app.db.models.program import Program
from backend.app.db.models.section import Section
from backend.app.db.models.faculty import Faculty
from backend.app.db.models.student import Student
from backend.app.db.models.subject import Subject
from backend.app.db.models.faculty_assignment import FacultyAssignment
from backend.app.db.models.student_enrollment import StudentEnrollment
from backend.app.core.security import hash_password


def get_or_create(db, model, filters, values):
    statement = select(model).filter_by(**filters)
    obj = db.scalar(statement)

    if obj:
        return obj, False

    obj = model(**values)
    db.add(obj)
    db.flush()
    return obj, True


def seed():
    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # 1. Department
        # ---------------------------------------------------------
        department, _ = get_or_create(
            db,
            Department,
            {"code": "CSE"},
            {
                "name": "Computer Science and Engineering",
                "code": "CSE",
            },
        )

        # ---------------------------------------------------------
        # 2. Academic Term
        # ---------------------------------------------------------
        term, _ = get_or_create(
            db,
            AcademicTerm,
            {
                "academic_year": "2026-2027",
                "semester": 7,
            },
            {
                "academic_year": "2026-2027",
                "semester": 7,
                "name": "Semester 7",
                "start_date": date(2026, 7, 1),
                "end_date": date(2026, 12, 31),
                "is_active": True,
            },
        )

        # ---------------------------------------------------------
        # 3. Program
        # ---------------------------------------------------------
        program, _ = get_or_create(
            db,
            Program,
            {"code": "BTECH-CSE"},
            {
                "department_id": department.id,
                "name": "B.Tech Computer Science and Engineering",
                "code": "BTECH-CSE",
            },
        )

        # ---------------------------------------------------------
        # 4. Section
        # ---------------------------------------------------------
        section, _ = get_or_create(
            db,
            Section,
            {
                "program_id": program.id,
                "academic_term_id": term.id,
                "name": "A",
            },
            {
                "program_id": program.id,
                "academic_term_id": term.id,
                "name": "A",
            },
        )

        # ---------------------------------------------------------
        # 5. Existing Faculty User
        # ---------------------------------------------------------
        faculty_user = db.scalar(
            select(User).where(User.username == "testfaculty")
        )

        if faculty_user is None:
            faculty_user = User(
                username="testfaculty",
                email="testfaculty@smartattendance.local",
                password_hash=hash_password("Faculty@123"),
                role="FACULTY",
                is_active=True,
            )
            db.add(faculty_user)
            db.flush()

        # ---------------------------------------------------------
        # 6. Faculty Profile
        # ---------------------------------------------------------
        faculty, _ = get_or_create(
            db,
            Faculty,
            {"user_id": faculty_user.id},
            {
                "user_id": faculty_user.id,
                "department_id": department.id,
                "employee_identifier": "FAC-001",
                "first_name": "Test",
                "last_name": "Faculty",
                "is_active": True,
            },
        )

        # ---------------------------------------------------------
        # 7. Student User
        # ---------------------------------------------------------
        student_user = db.scalar(
            select(User).where(User.username == "teststudent")
        )

        if student_user is None:
            student_user = User(
                username="teststudent",
                email="teststudent@smartattendance.local",
                password_hash=hash_password("Student@123"),
                role="STUDENT",
                is_active=True,
            )
            db.add(student_user)
            db.flush()

        # ---------------------------------------------------------
        # 8. Student Profile
        # ---------------------------------------------------------
        student, _ = get_or_create(
            db,
            Student,
            {"user_id": student_user.id},
            {
                "user_id": student_user.id,
                "department_id": department.id,
                "section_id": section.id,
                "student_identifier": "STU-001",
                "enrollment_number": "CSE2026-001",
                "first_name": "Test",
                "last_name": "Student",
                "date_of_birth": date(2005, 1, 15),
                "admission_year": 2026,
                "is_active": True,
            },
        )

        # ---------------------------------------------------------
        # 9. Subject
        # ---------------------------------------------------------
        subject, _ = get_or_create(
            db,
            Subject,
            {"subject_code": "CS701"},
            {
                "department_id": department.id,
                "subject_code": "CS701",
                "name": "Advanced Computer Science",
                "credits": 4,
                "is_active": True,
            },
        )

        # ---------------------------------------------------------
        # 10. Faculty Assignment
        # ---------------------------------------------------------
        assignment, _ = get_or_create(
            db,
            FacultyAssignment,
            {
                "faculty_id": faculty.id,
                "subject_id": subject.id,
                "section_id": section.id,
                "academic_term_id": term.id,
            },
            {
                "faculty_id": faculty.id,
                "subject_id": subject.id,
                "section_id": section.id,
                "academic_term_id": term.id,
            },
        )

        # ---------------------------------------------------------
        # 11. Student Enrollment
        # ---------------------------------------------------------
        enrollment, _ = get_or_create(
            db,
            StudentEnrollment,
            {
                "student_id": student.id,
                "subject_id": subject.id,
                "section_id": section.id,
                "academic_term_id": term.id,
            },
            {
                "student_id": student.id,
                "subject_id": subject.id,
                "section_id": section.id,
                "academic_term_id": term.id,
            },
        )

        db.commit()

        print("\nDevelopment data seeded successfully!\n")

        print(f"Department ID:        {department.id}")
        print(f"Academic Term ID:     {term.id}")
        print(f"Program ID:           {program.id}")
        print(f"Section ID:           {section.id}")
        print(f"Faculty ID:           {faculty.id}")
        print(f"Student ID:           {student.id}")
        print(f"Subject ID:           {subject.id}")
        print(f"Assignment ID:        {assignment.id}")
        print(f"Enrollment ID:        {enrollment.id}")

        print("\nDevelopment login credentials:")
        print("Faculty:")
        print("  username: testfaculty")
        print("  password: Faculty@123")

        print("\nStudent:")
        print("  username: teststudent")
        print("  password: Student@123")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()