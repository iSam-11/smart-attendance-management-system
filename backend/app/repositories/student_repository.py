from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from backend.app.db.models.student import Student


class StudentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, student_id: int) -> Student | None:
        return self.db.get(Student, student_id)

    def get_by_user_id(self, user_id: int, exclude_id: int | None = None) -> Student | None:
        stmt = select(Student).where(Student.user_id == user_id)
        if exclude_id is not None:
            stmt = stmt.where(Student.id != exclude_id)
        return self.db.scalar(stmt)

    def get_by_student_identifier(
        self,
        student_identifier: str,
        exclude_id: int | None = None,
    ) -> Student | None:
        stmt = select(Student).where(Student.student_identifier == student_identifier)
        if exclude_id is not None:
            stmt = stmt.where(Student.id != exclude_id)
        return self.db.scalar(stmt)

    def get_by_enrollment_number(
        self,
        enrollment_number: str,
        exclude_id: int | None = None,
    ) -> Student | None:
        stmt = select(Student).where(Student.enrollment_number == enrollment_number)
        if exclude_id is not None:
            stmt = stmt.where(Student.id != exclude_id)
        return self.db.scalar(stmt)

    def list(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        department_id: int | None = None,
        section_id: int | None = None,
        is_active: bool | None = None,
    ) -> list[Student]:
        stmt = select(Student).order_by(Student.id)
        stmt = self._apply_filters(
            stmt,
            search=search,
            department_id=department_id,
            section_id=section_id,
            is_active=is_active,
        )
        return list(self.db.scalars(stmt.offset(offset).limit(limit)).all())

    def count(
        self,
        *,
        search: str | None = None,
        department_id: int | None = None,
        section_id: int | None = None,
        is_active: bool | None = None,
    ) -> int:
        stmt = select(func.count(Student.id))
        stmt = self._apply_filters(
            stmt,
            search=search,
            department_id=department_id,
            section_id=section_id,
            is_active=is_active,
        )
        return int(self.db.scalar(stmt) or 0)

    def add(self, student: Student) -> Student:
        self.db.add(student)
        self.db.flush()
        return student

    def _apply_filters(
        self,
        stmt,
        *,
        search: str | None,
        department_id: int | None,
        section_id: int | None,
        is_active: bool | None,
    ):
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Student.student_identifier.ilike(pattern),
                    Student.enrollment_number.ilike(pattern),
                    Student.first_name.ilike(pattern),
                    Student.last_name.ilike(pattern),
                )
            )
        if department_id is not None:
            stmt = stmt.where(Student.department_id == department_id)
        if section_id is not None:
            stmt = stmt.where(Student.section_id == section_id)
        if is_active is not None:
            stmt = stmt.where(Student.is_active == is_active)
        return stmt
