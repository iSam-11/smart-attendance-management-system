from __future__ import annotations

from datetime import date
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from backend.app.db.models.attendance_session import AttendanceSession
from backend.app.db.models.faculty_assignment import FacultyAssignment
from backend.app.db.models.section import Section
from backend.app.db.models.student import Student
from backend.app.db.models.student_attendance import StudentAttendance
from backend.app.db.models.student_enrollment import StudentEnrollment
from backend.app.db.models.subject import Subject


class ReportRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_enrollment_attendance_data(
        self,
        *,
        student_id: int | None = None,
        subject_id: int | None = None,
        section_id: int | None = None,
        academic_term_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        allowed_assignments: list[tuple[int, int, int]] | None = None,
    ) -> list[dict]:
        conducted_stmt = (
            select(func.count(AttendanceSession.id))
            .join(FacultyAssignment, AttendanceSession.faculty_assignment_id == FacultyAssignment.id)
            .where(
                FacultyAssignment.subject_id == StudentEnrollment.subject_id,
                FacultyAssignment.section_id == StudentEnrollment.section_id,
                FacultyAssignment.academic_term_id == StudentEnrollment.academic_term_id,
            )
        )
        if start_date is not None:
            conducted_stmt = conducted_stmt.where(AttendanceSession.session_date >= start_date)
        if end_date is not None:
            conducted_stmt = conducted_stmt.where(AttendanceSession.session_date <= end_date)
        conducted_sub = conducted_stmt.scalar_subquery()

        present_stmt = (
            select(func.count(StudentAttendance.id))
            .join(AttendanceSession, StudentAttendance.attendance_session_id == AttendanceSession.id)
            .join(FacultyAssignment, AttendanceSession.faculty_assignment_id == FacultyAssignment.id)
            .where(
                StudentAttendance.student_id == StudentEnrollment.student_id,
                FacultyAssignment.subject_id == StudentEnrollment.subject_id,
                FacultyAssignment.section_id == StudentEnrollment.section_id,
                FacultyAssignment.academic_term_id == StudentEnrollment.academic_term_id,
                StudentAttendance.status == "PRESENT",
            )
        )
        if start_date is not None:
            present_stmt = present_stmt.where(AttendanceSession.session_date >= start_date)
        if end_date is not None:
            present_stmt = present_stmt.where(AttendanceSession.session_date <= end_date)
        present_sub = present_stmt.scalar_subquery()

        absent_stmt = (
            select(func.count(StudentAttendance.id))
            .join(AttendanceSession, StudentAttendance.attendance_session_id == AttendanceSession.id)
            .join(FacultyAssignment, AttendanceSession.faculty_assignment_id == FacultyAssignment.id)
            .where(
                StudentAttendance.student_id == StudentEnrollment.student_id,
                FacultyAssignment.subject_id == StudentEnrollment.subject_id,
                FacultyAssignment.section_id == StudentEnrollment.section_id,
                FacultyAssignment.academic_term_id == StudentEnrollment.academic_term_id,
                StudentAttendance.status == "ABSENT",
            )
        )
        if start_date is not None:
            absent_stmt = absent_stmt.where(AttendanceSession.session_date >= start_date)
        if end_date is not None:
            absent_stmt = absent_stmt.where(AttendanceSession.session_date <= end_date)
        absent_sub = absent_stmt.scalar_subquery()

        stmt = (
            select(
                StudentEnrollment.student_id,
                Student.first_name,
                Student.last_name,
                Student.enrollment_number,
                StudentEnrollment.subject_id,
                Subject.name.label("subject_name"),
                Subject.subject_code,
                StudentEnrollment.section_id,
                Section.name.label("section_name"),
                StudentEnrollment.academic_term_id,
                conducted_sub.label("total_conducted"),
                present_sub.label("present_classes"),
                absent_sub.label("absent_classes"),
            )
            .join(Student, StudentEnrollment.student_id == Student.id)
            .join(Subject, StudentEnrollment.subject_id == Subject.id)
            .join(Section, StudentEnrollment.section_id == Section.id)
            .order_by(StudentEnrollment.student_id, StudentEnrollment.subject_id)
        )

        if student_id is not None:
            stmt = stmt.where(StudentEnrollment.student_id == student_id)
        if subject_id is not None:
            stmt = stmt.where(StudentEnrollment.subject_id == subject_id)
        if section_id is not None:
            stmt = stmt.where(StudentEnrollment.section_id == section_id)
        if academic_term_id is not None:
            stmt = stmt.where(StudentEnrollment.academic_term_id == academic_term_id)

        if allowed_assignments is not None:
            if not allowed_assignments:
                return []
            conditions = [
                and_(
                    StudentEnrollment.subject_id == sub_id,
                    StudentEnrollment.section_id == sec_id,
                    StudentEnrollment.academic_term_id == term_id,
                )
                for sub_id, sec_id, term_id in allowed_assignments
            ]
            stmt = stmt.where(or_(*conditions))

        results = self.db.execute(stmt).all()

        rows = []
        for r in results:
            first_name = r.first_name or ""
            last_name = r.last_name or ""
            full_name = f"{first_name} {last_name}".strip()

            rows.append({
                "student_id": r.student_id,
                "student_name": full_name,
                "enrollment_number": r.enrollment_number,
                "subject_id": r.subject_id,
                "subject_name": r.subject_name,
                "subject_code": r.subject_code,
                "section_id": r.section_id,
                "section_name": r.section_name,
                "academic_term_id": r.academic_term_id,
                "total_conducted_classes": r.total_conducted or 0,
                "present_classes": r.present_classes or 0,
                "absent_classes": r.absent_classes or 0,
            })
        return rows
