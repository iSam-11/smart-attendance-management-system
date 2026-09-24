from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.db.models.faculty_assignment import FacultyAssignment
from backend.app.db.models.section import Section
from backend.app.db.models.student import Student
from backend.app.db.models.student_enrollment import StudentEnrollment


class SectionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, section_id: int) -> Section | None:
        return self.db.get(Section, section_id)

    def get_by_identity(
        self,
        program_id: int,
        academic_term_id: int,
        name: str,
        exclude_id: int | None = None,
    ) -> Section | None:
        stmt = select(Section).where(
            Section.program_id == program_id,
            Section.academic_term_id == academic_term_id,
            Section.name == name,
        )
        if exclude_id is not None:
            stmt = stmt.where(Section.id != exclude_id)
        return self.db.scalar(stmt)

    def list(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        program_id: int | None = None,
        academic_term_id: int | None = None,
    ) -> list[Section]:
        stmt = select(Section).order_by(Section.id)
        if search:
            stmt = stmt.where(Section.name.ilike(f"%{search}%"))
        if program_id is not None:
            stmt = stmt.where(Section.program_id == program_id)
        if academic_term_id is not None:
            stmt = stmt.where(Section.academic_term_id == academic_term_id)
        return list(self.db.scalars(stmt.offset(offset).limit(limit)).all())

    def count(
        self,
        *,
        search: str | None = None,
        program_id: int | None = None,
        academic_term_id: int | None = None,
    ) -> int:
        stmt = select(func.count(Section.id))
        if search:
            stmt = stmt.where(Section.name.ilike(f"%{search}%"))
        if program_id is not None:
            stmt = stmt.where(Section.program_id == program_id)
        if academic_term_id is not None:
            stmt = stmt.where(Section.academic_term_id == academic_term_id)
        return int(self.db.scalar(stmt) or 0)

    def add(self, section: Section) -> Section:
        self.db.add(section)
        self.db.flush()
        return section

    def delete(self, section: Section) -> None:
        self.db.delete(section)
        self.db.flush()

    def is_in_use(self, section_id: int) -> bool:
        student_count = self.db.scalar(
            select(func.count(Student.id)).where(Student.section_id == section_id)
        )
        assignment_count = self.db.scalar(
            select(func.count(FacultyAssignment.id)).where(
                FacultyAssignment.section_id == section_id
            )
        )
        enrollment_count = self.db.scalar(
            select(func.count(StudentEnrollment.id)).where(
                StudentEnrollment.section_id == section_id
            )
        )
        return (
            int(student_count or 0) > 0
            or int(assignment_count or 0) > 0
            or int(enrollment_count or 0) > 0
        )
