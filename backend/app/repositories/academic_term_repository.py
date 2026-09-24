from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from backend.app.db.models.academic_term import AcademicTerm
from backend.app.db.models.faculty_assignment import FacultyAssignment
from backend.app.db.models.section import Section
from backend.app.db.models.student_enrollment import StudentEnrollment


class AcademicTermRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, term_id: int) -> AcademicTerm | None:
        return self.db.get(AcademicTerm, term_id)

    def get_by_year_and_semester(
        self,
        academic_year: str,
        semester: str,
        exclude_id: int | None = None,
    ) -> AcademicTerm | None:
        stmt = select(AcademicTerm).where(
            AcademicTerm.academic_year == academic_year,
            AcademicTerm.semester == semester,
        )
        if exclude_id is not None:
            stmt = stmt.where(AcademicTerm.id != exclude_id)
        return self.db.scalar(stmt)

    def list(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> list[AcademicTerm]:
        stmt = select(AcademicTerm).order_by(AcademicTerm.id)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    AcademicTerm.name.ilike(pattern),
                    AcademicTerm.academic_year.ilike(pattern),
                    AcademicTerm.semester.ilike(pattern),
                )
            )
        if is_active is not None:
            stmt = stmt.where(AcademicTerm.is_active == is_active)
        return list(self.db.scalars(stmt.offset(offset).limit(limit)).all())

    def count(
        self,
        *,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> int:
        stmt = select(func.count(AcademicTerm.id))
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    AcademicTerm.name.ilike(pattern),
                    AcademicTerm.academic_year.ilike(pattern),
                    AcademicTerm.semester.ilike(pattern),
                )
            )
        if is_active is not None:
            stmt = stmt.where(AcademicTerm.is_active == is_active)
        return int(self.db.scalar(stmt) or 0)

    def add(self, term: AcademicTerm) -> AcademicTerm:
        self.db.add(term)
        self.db.flush()
        return term

    def delete(self, term: AcademicTerm) -> None:
        self.db.delete(term)
        self.db.flush()

    def is_in_use(self, term_id: int) -> bool:
        section_count = self.db.scalar(
            select(func.count(Section.id)).where(Section.academic_term_id == term_id)
        )
        assignment_count = self.db.scalar(
            select(func.count(FacultyAssignment.id)).where(
                FacultyAssignment.academic_term_id == term_id
            )
        )
        enrollment_count = self.db.scalar(
            select(func.count(StudentEnrollment.id)).where(
                StudentEnrollment.academic_term_id == term_id
            )
        )
        return (
            int(section_count or 0) > 0
            or int(assignment_count or 0) > 0
            or int(enrollment_count or 0) > 0
        )
