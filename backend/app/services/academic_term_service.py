from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.exceptions import ConflictError, NotFoundError
from backend.app.db.models.academic_term import AcademicTerm
from backend.app.repositories.academic_term_repository import AcademicTermRepository
from backend.app.schemas.academic_term import (
    AcademicTermCreate,
    AcademicTermRead,
    AcademicTermUpdate,
)
from backend.app.schemas.common import PaginatedResponse, PaginationParams


class AcademicTermService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AcademicTermRepository(db)

    def create(self, payload: AcademicTermCreate) -> AcademicTermRead:
        self._ensure_unique(payload.academic_year, payload.semester)
        term = AcademicTerm(
            academic_year=payload.academic_year,
            semester=payload.semester,
            name=payload.name,
            start_date=payload.start_date,
            end_date=payload.end_date,
            is_active=payload.is_active,
        )
        self.repository.add(term)
        self._commit("Academic term already exists")
        return AcademicTermRead.model_validate(term)

    def get(self, term_id: int) -> AcademicTermRead:
        return AcademicTermRead.model_validate(self._get_or_404(term_id))

    def list(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> PaginatedResponse[AcademicTermRead]:
        items = self.repository.list(
            offset=pagination.offset,
            limit=pagination.page_size,
            search=search,
            is_active=is_active,
        )
        total = self.repository.count(search=search, is_active=is_active)
        return PaginatedResponse[AcademicTermRead](
            items=[AcademicTermRead.model_validate(item) for item in items],
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
        )

    def update(self, term_id: int, payload: AcademicTermUpdate) -> AcademicTermRead:
        term = self._get_or_404(term_id)
        self._ensure_unique(
            payload.academic_year,
            payload.semester,
            exclude_id=term_id,
        )
        term.academic_year = payload.academic_year
        term.semester = payload.semester
        term.name = payload.name
        term.start_date = payload.start_date
        term.end_date = payload.end_date
        term.is_active = payload.is_active
        self._commit("Academic term already exists")
        return AcademicTermRead.model_validate(term)

    def delete(self, term_id: int) -> None:
        term = self._get_or_404(term_id)
        if self.repository.is_in_use(term_id):
            raise ConflictError("Cannot delete an academic term that is in use")
        self.repository.delete(term)
        self._commit("Cannot delete academic term")

    def _get_or_404(self, term_id: int) -> AcademicTerm:
        term = self.repository.get_by_id(term_id)
        if term is None:
            raise NotFoundError("Academic term not found")
        return term

    def _ensure_unique(
        self,
        academic_year: str,
        semester: str,
        exclude_id: int | None = None,
    ) -> None:
        existing = self.repository.get_by_year_and_semester(
            academic_year,
            semester,
            exclude_id=exclude_id,
        )
        if existing is not None:
            raise ConflictError(
                "An academic term already exists for this year and semester"
            )

    def _commit(self, conflict_message: str) -> None:
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictError(conflict_message)
