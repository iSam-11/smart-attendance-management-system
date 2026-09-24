from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.exceptions import ConflictError, NotFoundError
from backend.app.db.models.subject import Subject
from backend.app.repositories.department_repository import DepartmentRepository
from backend.app.repositories.subject_repository import SubjectRepository
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.subject import SubjectCreate, SubjectRead, SubjectUpdate


class SubjectService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = SubjectRepository(db)
        self.departments = DepartmentRepository(db)

    def create(self, payload: SubjectCreate) -> SubjectRead:
        self._ensure_department_exists(payload.department_id)
        self._ensure_unique_code(payload.subject_code)
        subject = Subject(
            department_id=payload.department_id,
            subject_code=payload.subject_code,
            name=payload.name,
            credits=payload.credits,
            is_active=payload.is_active,
        )
        self.repository.add(subject)
        self._commit("Subject code already exists")
        return SubjectRead.model_validate(subject)

    def get(self, subject_id: int) -> SubjectRead:
        return SubjectRead.model_validate(self._get_or_404(subject_id))

    def list(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        department_id: int | None = None,
        is_active: bool | None = None,
    ) -> PaginatedResponse[SubjectRead]:
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
        return PaginatedResponse[SubjectRead](
            items=[SubjectRead.model_validate(item) for item in items],
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
        )

    def update(self, subject_id: int, payload: SubjectUpdate) -> SubjectRead:
        subject = self._get_or_404(subject_id)
        self._ensure_department_exists(payload.department_id)
        self._ensure_unique_code(payload.subject_code, exclude_id=subject_id)
        subject.department_id = payload.department_id
        subject.subject_code = payload.subject_code
        subject.name = payload.name
        subject.credits = payload.credits
        subject.is_active = payload.is_active
        self._commit("Subject code already exists")
        return SubjectRead.model_validate(subject)

    def delete(self, subject_id: int) -> None:
        subject = self._get_or_404(subject_id)
        if self.repository.is_in_use(subject_id):
            raise ConflictError("Cannot delete a subject that is in use")
        self.repository.delete(subject)
        self._commit("Cannot delete subject")

    def _get_or_404(self, subject_id: int) -> Subject:
        subject = self.repository.get_by_id(subject_id)
        if subject is None:
            raise NotFoundError("Subject not found")
        return subject

    def _ensure_department_exists(self, department_id: int) -> None:
        if self.departments.get_by_id(department_id) is None:
            raise NotFoundError("Department not found")

    def _ensure_unique_code(self, subject_code: str, exclude_id: int | None = None) -> None:
        if self.repository.get_by_code(subject_code, exclude_id=exclude_id):
            raise ConflictError("Subject code already exists")

    def _commit(self, conflict_message: str) -> None:
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictError(conflict_message)
