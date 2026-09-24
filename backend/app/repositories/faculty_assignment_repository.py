from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.db.models.attendance_session import AttendanceSession
from backend.app.db.models.faculty_assignment import FacultyAssignment


class FacultyAssignmentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, assignment_id: int) -> FacultyAssignment | None:
        return self.db.get(FacultyAssignment, assignment_id)

    def get_by_unique_composite(
        self,
        faculty_id: int,
        subject_id: int,
        section_id: int,
        academic_term_id: int,
        exclude_id: int | None = None,
    ) -> FacultyAssignment | None:
        stmt = select(FacultyAssignment).where(
            FacultyAssignment.faculty_id == faculty_id,
            FacultyAssignment.subject_id == subject_id,
            FacultyAssignment.section_id == section_id,
            FacultyAssignment.academic_term_id == academic_term_id,
        )
        if exclude_id is not None:
            stmt = stmt.where(FacultyAssignment.id != exclude_id)
        return self.db.scalar(stmt)

    def list(
        self,
        *,
        offset: int,
        limit: int,
        faculty_id: int | None = None,
        subject_id: int | None = None,
        section_id: int | None = None,
        academic_term_id: int | None = None,
    ) -> list[FacultyAssignment]:
        stmt = select(FacultyAssignment).order_by(FacultyAssignment.id)
        stmt = self._apply_filters(
            stmt,
            faculty_id=faculty_id,
            subject_id=subject_id,
            section_id=section_id,
            academic_term_id=academic_term_id,
        )
        return list(self.db.scalars(stmt.offset(offset).limit(limit)).all())

    def count(
        self,
        *,
        faculty_id: int | None = None,
        subject_id: int | None = None,
        section_id: int | None = None,
        academic_term_id: int | None = None,
    ) -> int:
        stmt = select(func.count(FacultyAssignment.id))
        stmt = self._apply_filters(
            stmt,
            faculty_id=faculty_id,
            subject_id=subject_id,
            section_id=section_id,
            academic_term_id=academic_term_id,
        )
        return int(self.db.scalar(stmt) or 0)

    def add(self, assignment: FacultyAssignment) -> FacultyAssignment:
        self.db.add(assignment)
        self.db.flush()
        return assignment

    def delete(self, assignment: FacultyAssignment) -> None:
        self.db.delete(assignment)
        self.db.flush()

    def is_in_use(self, assignment_id: int) -> bool:
        session_count = self.db.scalar(
            select(func.count(AttendanceSession.id)).where(
                AttendanceSession.faculty_assignment_id == assignment_id
            )
        )
        return int(session_count or 0) > 0

    def _apply_filters(
        self,
        stmt,
        *,
        faculty_id: int | None,
        subject_id: int | None,
        section_id: int | None,
        academic_term_id: int | None,
    ):
        if faculty_id is not None:
            stmt = stmt.where(FacultyAssignment.faculty_id == faculty_id)
        if subject_id is not None:
            stmt = stmt.where(FacultyAssignment.subject_id == subject_id)
        if section_id is not None:
            stmt = stmt.where(FacultyAssignment.section_id == section_id)
        if academic_term_id is not None:
            stmt = stmt.where(FacultyAssignment.academic_term_id == academic_term_id)
        return stmt
