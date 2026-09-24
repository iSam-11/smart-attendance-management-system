from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from backend.app.db.models.faculty import Faculty


class FacultyRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, faculty_id: int) -> Faculty | None:
        return self.db.get(Faculty, faculty_id)

    def get_by_user_id(self, user_id: int, exclude_id: int | None = None) -> Faculty | None:
        stmt = select(Faculty).where(Faculty.user_id == user_id)
        if exclude_id is not None:
            stmt = stmt.where(Faculty.id != exclude_id)
        return self.db.scalar(stmt)

    def get_by_employee_identifier(
        self,
        employee_identifier: str,
        exclude_id: int | None = None,
    ) -> Faculty | None:
        stmt = select(Faculty).where(Faculty.employee_identifier == employee_identifier)
        if exclude_id is not None:
            stmt = stmt.where(Faculty.id != exclude_id)
        return self.db.scalar(stmt)

    def list(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        department_id: int | None = None,
        is_active: bool | None = None,
    ) -> list[Faculty]:
        stmt = select(Faculty).order_by(Faculty.id)
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
        stmt = select(func.count(Faculty.id))
        stmt = self._apply_filters(
            stmt,
            search=search,
            department_id=department_id,
            is_active=is_active,
        )
        return int(self.db.scalar(stmt) or 0)

    def add(self, faculty: Faculty) -> Faculty:
        self.db.add(faculty)
        self.db.flush()
        return faculty

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
                or_(
                    Faculty.employee_identifier.ilike(pattern),
                    Faculty.first_name.ilike(pattern),
                    Faculty.last_name.ilike(pattern),
                )
            )
        if department_id is not None:
            stmt = stmt.where(Faculty.department_id == department_id)
        if is_active is not None:
            stmt = stmt.where(Faculty.is_active == is_active)
        return stmt
