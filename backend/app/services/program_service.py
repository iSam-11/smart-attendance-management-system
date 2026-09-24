from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.exceptions import ConflictError, NotFoundError
from backend.app.db.models.program import Program
from backend.app.repositories.department_repository import DepartmentRepository
from backend.app.repositories.program_repository import ProgramRepository
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.program import ProgramCreate, ProgramRead, ProgramUpdate


class ProgramService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = ProgramRepository(db)
        self.departments = DepartmentRepository(db)

    def create(self, payload: ProgramCreate) -> ProgramRead:
        self._ensure_department_exists(payload.department_id)
        self._ensure_unique_code(payload.code)
        program = Program(
            department_id=payload.department_id,
            name=payload.name,
            code=payload.code,
        )
        self.repository.add(program)
        self._commit("Program code already exists")
        return ProgramRead.model_validate(program)

    def get(self, program_id: int) -> ProgramRead:
        return ProgramRead.model_validate(self._get_or_404(program_id))

    def list(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        department_id: int | None = None,
    ) -> PaginatedResponse[ProgramRead]:
        items = self.repository.list(
            offset=pagination.offset,
            limit=pagination.page_size,
            search=search,
            department_id=department_id,
        )
        total = self.repository.count(search=search, department_id=department_id)
        return PaginatedResponse[ProgramRead](
            items=[ProgramRead.model_validate(item) for item in items],
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
        )

    def update(self, program_id: int, payload: ProgramUpdate) -> ProgramRead:
        program = self._get_or_404(program_id)
        self._ensure_department_exists(payload.department_id)
        self._ensure_unique_code(payload.code, exclude_id=program_id)
        program.department_id = payload.department_id
        program.name = payload.name
        program.code = payload.code
        self._commit("Program code already exists")
        return ProgramRead.model_validate(program)

    def delete(self, program_id: int) -> None:
        program = self._get_or_404(program_id)
        if self.repository.has_sections(program_id):
            raise ConflictError("Cannot delete a program that has sections")
        self.repository.delete(program)
        self._commit("Cannot delete program")

    def _get_or_404(self, program_id: int) -> Program:
        program = self.repository.get_by_id(program_id)
        if program is None:
            raise NotFoundError("Program not found")
        return program

    def _ensure_department_exists(self, department_id: int) -> None:
        if self.departments.get_by_id(department_id) is None:
            raise NotFoundError("Department not found")

    def _ensure_unique_code(self, code: str, exclude_id: int | None = None) -> None:
        if self.repository.get_by_code(code, exclude_id=exclude_id):
            raise ConflictError("Program code already exists")

    def _commit(self, conflict_message: str) -> None:
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictError(conflict_message)
