from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.db.models.student_enrollment import StudentEnrollment


class StudentEnrollmentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, enrollment_id: int) -> StudentEnrollment | None:
        return self.db.get(StudentEnrollment, enrollment_id)

    def get_by_unique_composite(
        self,
        student_id: int,
        subject_id: int,
        section_id: int,
        academic_term_id: int,
        exclude_id: int | None = None,
    ) -> StudentEnrollment | None:
        stmt = select(StudentEnrollment).where(
            StudentEnrollment.student_id == student_id,
            StudentEnrollment.subject_id == subject_id,
            StudentEnrollment.section_id == section_id,
            StudentEnrollment.academic_term_id == academic_term_id,
        )
        if exclude_id is not None:
            stmt = stmt.where(StudentEnrollment.id != exclude_id)
        return self.db.scalar(stmt)

    def list(
        self,
        *,
        offset: int,
        limit: int,
        student_id: int | None = None,
        subject_id: int | None = None,
        section_id: int | None = None,
        academic_term_id: int | None = None,
    ) -> list[StudentEnrollment]:
        stmt = select(StudentEnrollment).order_by(StudentEnrollment.id)
        stmt = self._apply_filters(
            stmt,
            student_id=student_id,
            subject_id=subject_id,
            section_id=section_id,
            academic_term_id=academic_term_id,
        )
        return list(self.db.scalars(stmt.offset(offset).limit(limit)).all())

    def count(
        self,
        *,
        student_id: int | None = None,
        subject_id: int | None = None,
        section_id: int | None = None,
        academic_term_id: int | None = None,
    ) -> int:
        stmt = select(func.count(StudentEnrollment.id))
        stmt = self._apply_filters(
            stmt,
            student_id=student_id,
            subject_id=subject_id,
            section_id=section_id,
            academic_term_id=academic_term_id,
        )
        return int(self.db.scalar(stmt) or 0)

    def add(self, enrollment: StudentEnrollment) -> StudentEnrollment:
        self.db.add(enrollment)
        self.db.flush()
        return enrollment

    def delete(self, enrollment: StudentEnrollment) -> None:
        self.db.delete(enrollment)
        self.db.flush()

    def _apply_filters(
        self,
        stmt,
        *,
        student_id: int | None,
        subject_id: int | None,
        section_id: int | None,
        academic_term_id: int | None,
    ):
        if student_id is not None:
            stmt = stmt.where(StudentEnrollment.student_id == student_id)
        if subject_id is not None:
            stmt = stmt.where(StudentEnrollment.subject_id == subject_id)
        if section_id is not None:
            stmt = stmt.where(StudentEnrollment.section_id == section_id)
        if academic_term_id is not None:
            stmt = stmt.where(StudentEnrollment.academic_term_id == academic_term_id)
        return stmt
