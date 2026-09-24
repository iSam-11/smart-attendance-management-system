from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from backend.app.db.models.program import Program
from backend.app.db.models.section import Section


class ProgramRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, program_id: int) -> Program | None:
        return self.db.get(Program, program_id)

    def get_by_code(self, code: str, exclude_id: int | None = None) -> Program | None:
        stmt = select(Program).where(Program.code == code)
        if exclude_id is not None:
            stmt = stmt.where(Program.id != exclude_id)
        return self.db.scalar(stmt)

    def list(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        department_id: int | None = None,
    ) -> list[Program]:
        stmt = select(Program).order_by(Program.id)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(Program.name.ilike(pattern), Program.code.ilike(pattern))
            )
        if department_id is not None:
            stmt = stmt.where(Program.department_id == department_id)
        return list(self.db.scalars(stmt.offset(offset).limit(limit)).all())

    def count(
        self,
        *,
        search: str | None = None,
        department_id: int | None = None,
    ) -> int:
        stmt = select(func.count(Program.id))
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(Program.name.ilike(pattern), Program.code.ilike(pattern))
            )
        if department_id is not None:
            stmt = stmt.where(Program.department_id == department_id)
        return int(self.db.scalar(stmt) or 0)

    def add(self, program: Program) -> Program:
        self.db.add(program)
        self.db.flush()
        return program

    def delete(self, program: Program) -> None:
        self.db.delete(program)
        self.db.flush()

    def has_sections(self, program_id: int) -> bool:
        stmt = select(func.count(Section.id)).where(Section.program_id == program_id)
        return int(self.db.scalar(stmt) or 0) > 0
