from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from backend.app.db.models.department import Department
from backend.app.db.models.program import Program


class DepartmentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, department_id: int) -> Department | None:
        return self.db.get(Department, department_id)

    def get_by_code(self, code: str, exclude_id: int | None = None) -> Department | None:
        stmt = select(Department).where(Department.code == code)
        if exclude_id is not None:
            stmt = stmt.where(Department.id != exclude_id)
        return self.db.scalar(stmt)

    def get_by_name(self, name: str, exclude_id: int | None = None) -> Department | None:
        stmt = select(Department).where(Department.name == name)
        if exclude_id is not None:
            stmt = stmt.where(Department.id != exclude_id)
        return self.db.scalar(stmt)

    def list(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
    ) -> list[Department]:
        stmt = select(Department).order_by(Department.id)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(Department.name.ilike(pattern), Department.code.ilike(pattern))
            )
        return list(self.db.scalars(stmt.offset(offset).limit(limit)).all())

    def count(self, *, search: str | None = None) -> int:
        stmt = select(func.count(Department.id))
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(Department.name.ilike(pattern), Department.code.ilike(pattern))
            )
        return int(self.db.scalar(stmt) or 0)

    def add(self, department: Department) -> Department:
        self.db.add(department)
        self.db.flush()
        return department

    def delete(self, department: Department) -> None:
        self.db.delete(department)
        self.db.flush()

    def has_programs(self, department_id: int) -> bool:
        stmt = select(func.count(Program.id)).where(Program.department_id == department_id)
        return int(self.db.scalar(stmt) or 0) > 0
