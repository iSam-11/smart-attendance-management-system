from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.exceptions import ConflictError, NotFoundError
from backend.app.db.models.department import Department
from backend.app.repositories.department_repository import DepartmentRepository
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.department import DepartmentCreate, DepartmentRead, DepartmentUpdate


class DepartmentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = DepartmentRepository(db)

    def create(self, payload: DepartmentCreate) -> DepartmentRead:
        self._ensure_unique(payload.name, payload.code)
        department = Department(name=payload.name, code=payload.code)
        self.repository.add(department)
        self._commit("Department code or name already exists")
        return DepartmentRead.model_validate(department)

    def get(self, department_id: int) -> DepartmentRead:
        return DepartmentRead.model_validate(self._get_or_404(department_id))

    def list(
        self,
        pagination: PaginationParams,
        search: str | None = None,
    ) -> PaginatedResponse[DepartmentRead]:
        items = self.repository.list(
            offset=pagination.offset,
            limit=pagination.page_size,
            search=search,
        )
        total = self.repository.count(search=search)
        return PaginatedResponse[DepartmentRead](
            items=[DepartmentRead.model_validate(item) for item in items],
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
        )

    def update(self, department_id: int, payload: DepartmentUpdate) -> DepartmentRead:
        department = self._get_or_404(department_id)
        self._ensure_unique(payload.name, payload.code, exclude_id=department_id)
        department.name = payload.name
        department.code = payload.code
        self._commit("Department code or name already exists")
        return DepartmentRead.model_validate(department)

    def delete(self, department_id: int) -> None:
        department = self._get_or_404(department_id)
        if self.repository.has_programs(department_id):
            raise ConflictError("Cannot delete a department that has programs")
        self.repository.delete(department)
        self._commit("Cannot delete department")

    def _get_or_404(self, department_id: int) -> Department:
        department = self.repository.get_by_id(department_id)
        if department is None:
            raise NotFoundError("Department not found")
        return department

    def _ensure_unique(
        self,
        name: str,
        code: str,
        exclude_id: int | None = None,
    ) -> None:
        if self.repository.get_by_code(code, exclude_id=exclude_id):
            raise ConflictError("Department code already exists")
        if self.repository.get_by_name(name, exclude_id=exclude_id):
            raise ConflictError("Department name already exists")

    def _commit(self, conflict_message: str) -> None:
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictError(conflict_message)
