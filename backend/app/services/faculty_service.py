from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.constants import ROLE_FACULTY
from backend.app.core.exceptions import ConflictError, DomainValidationError, NotFoundError
from backend.app.db.models.faculty import Faculty
from backend.app.repositories.department_repository import DepartmentRepository
from backend.app.repositories.faculty_repository import FacultyRepository
from backend.app.repositories.user_repository import get_user_by_id
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.faculty import FacultyCreate, FacultyRead, FacultyUpdate


class FacultyService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = FacultyRepository(db)
        self.departments = DepartmentRepository(db)

    def create(self, payload: FacultyCreate) -> FacultyRead:
        self._validate_relations(payload)
        self._ensure_unique(payload.user_id, payload.employee_identifier)
        faculty = Faculty(
            user_id=payload.user_id,
            department_id=payload.department_id,
            employee_identifier=payload.employee_identifier,
            first_name=payload.first_name,
            last_name=payload.last_name,
            is_active=payload.is_active,
        )
        self.repository.add(faculty)
        self._commit("Employee identifier already exists")
        return FacultyRead.model_validate(faculty)

    def get(self, faculty_id: int) -> FacultyRead:
        return FacultyRead.model_validate(self._get_or_404(faculty_id))

    def list(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        department_id: int | None = None,
        is_active: bool | None = None,
    ) -> PaginatedResponse[FacultyRead]:
        items = self.repository.list(
            offset=pagination.offset,
            limit=pagination.page_size,
            search=search,
            department_id=department_id,
            is_active=is_active,
        )
        total = self.repository.count(
            search=search,
            department_id=department_id,
            is_active=is_active,
        )
        return PaginatedResponse[FacultyRead](
            items=[FacultyRead.model_validate(item) for item in items],
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
        )

    def update(self, faculty_id: int, payload: FacultyUpdate) -> FacultyRead:
        faculty = self._get_or_404(faculty_id)
        self._validate_relations(payload)
        self._ensure_unique(
            payload.user_id,
            payload.employee_identifier,
            exclude_id=faculty_id,
        )
        faculty.user_id = payload.user_id
        faculty.department_id = payload.department_id
        faculty.employee_identifier = payload.employee_identifier
        faculty.first_name = payload.first_name
        faculty.last_name = payload.last_name
        faculty.is_active = payload.is_active
        self._commit("Employee identifier already exists")
        return FacultyRead.model_validate(faculty)

    def _get_or_404(self, faculty_id: int) -> Faculty:
        faculty = self.repository.get_by_id(faculty_id)
        if faculty is None:
            raise NotFoundError("Faculty not found")
        return faculty

    def _validate_relations(self, payload: FacultyCreate) -> None:
        user = get_user_by_id(self.db, payload.user_id)
        if user is None:
            raise NotFoundError("User not found")
        if user.role != ROLE_FACULTY:
            raise DomainValidationError("User must have the FACULTY role")
        if self.departments.get_by_id(payload.department_id) is None:
            raise NotFoundError("Department not found")

    def _ensure_unique(
        self,
        user_id: int,
        employee_identifier: str,
        exclude_id: int | None = None,
    ) -> None:
        if self.repository.get_by_user_id(user_id, exclude_id=exclude_id):
            raise ConflictError("A faculty profile already exists for this user")
        if self.repository.get_by_employee_identifier(
            employee_identifier, exclude_id=exclude_id
        ):
            raise ConflictError("Employee identifier already exists")

    def _commit(self, conflict_message: str) -> None:
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictError(conflict_message)
