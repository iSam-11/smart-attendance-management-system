from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from backend.app.db.models.faculty_assignment import FacultyAssignment
from backend.app.db.models.student_enrollment import StudentEnrollment
from backend.app.db.models.subject import Subject


class SubjectRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, subject_id: int) -> Subject | None:
        return self.db.get(Subject, subject_id)

    def get_by_code(self, subject_code: str, exclude_id: int | None = None) -> Subject | None:
        stmt = select(Subject).where(Subject.subject_code == subject_code)
        if exclude_id is not None:
            stmt = stmt.where(Subject.id != exclude_id)
        return self.db.scalar(stmt)

    def list(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        department_id: int | None = None,
        is_active: bool | None = None,
    ) -> list[Subject]:
        stmt = select(Subject).order_by(Subject.id)
        stmt = self._apply_filters(
            stmt,
            search=search,
            department_id=department_id,
            is_active=is_active,
        )
        return list(self.db.scalars(stmt.offset(offset).limit(limit)).all())

    def count(
        self,
        *,
        search: str | None = None,
        department_id: int | None = None,
        is_active: bool | None = None,
    ) -> int:
        stmt = select(func.count(Subject.id))
        stmt = self._apply_filters(
            stmt,
            search=search,
            department_id=department_id,
            is_active=is_active,
        )
        return int(self.db.scalar(stmt) or 0)

    def add(self, subject: Subject) -> Subject:
        self.db.add(subject)
        self.db.flush()
        return subject

    def delete(self, subject: Subject) -> None:
        self.db.delete(subject)
        self.db.flush()

    def is_in_use(self, subject_id: int) -> bool:
        assignment_count = self.db.scalar(
            select(func.count(FacultyAssignment.id)).where(
                FacultyAssignment.subject_id == subject_id
            )
        )
        enrollment_count = self.db.scalar(
            select(func.count(StudentEnrollment.id)).where(
                StudentEnrollment.subject_id == subject_id
            )
        )
        return int(assignment_count or 0) > 0 or int(enrollment_count or 0) > 0

    def _apply_filters(
        self,
        stmt,
        *,
        search: str | None,
        department_id: int | None,
        is_active: bool | None,
    ):
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(Subject.subject_code.ilike(pattern), Subject.name.ilike(pattern))
            )
        if department_id is not None:
            stmt = stmt.where(Subject.department_id == department_id)
        if is_active is not None:
            stmt = stmt.where(Subject.is_active == is_active)
        return stmt
