from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.exceptions import ConflictError, NotFoundError
from backend.app.db.models.section import Section
from backend.app.repositories.academic_term_repository import AcademicTermRepository
from backend.app.repositories.program_repository import ProgramRepository
from backend.app.repositories.section_repository import SectionRepository
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.section import SectionCreate, SectionRead, SectionUpdate


class SectionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = SectionRepository(db)
        self.programs = ProgramRepository(db)
        self.terms = AcademicTermRepository(db)

    def create(self, payload: SectionCreate) -> SectionRead:
        self._ensure_parents_exist(payload.program_id, payload.academic_term_id)
        self._ensure_unique(payload.program_id, payload.academic_term_id, payload.name)
        section = Section(
            program_id=payload.program_id,
            academic_term_id=payload.academic_term_id,
            name=payload.name,
        )
        self.repository.add(section)
        self._commit("Section already exists")
        return SectionRead.model_validate(section)

    def get(self, section_id: int) -> SectionRead:
        return SectionRead.model_validate(self._get_or_404(section_id))

    def list(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        program_id: int | None = None,
        academic_term_id: int | None = None,
    ) -> PaginatedResponse[SectionRead]:
        items = self.repository.list(
            offset=pagination.offset,
            limit=pagination.page_size,
            search=search,
            program_id=program_id,
            academic_term_id=academic_term_id,
        )
        total = self.repository.count(
            search=search,
            program_id=program_id,
            academic_term_id=academic_term_id,
        )
        return PaginatedResponse[SectionRead](
            items=[SectionRead.model_validate(item) for item in items],
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
        )

    def update(self, section_id: int, payload: SectionUpdate) -> SectionRead:
        section = self._get_or_404(section_id)
        self._ensure_parents_exist(payload.program_id, payload.academic_term_id)
        self._ensure_unique(
            payload.program_id,
            payload.academic_term_id,
            payload.name,
            exclude_id=section_id,
        )
        section.program_id = payload.program_id
        section.academic_term_id = payload.academic_term_id
        section.name = payload.name
        self._commit("Section already exists")
        return SectionRead.model_validate(section)

    def delete(self, section_id: int) -> None:
        section = self._get_or_404(section_id)
        if self.repository.is_in_use(section_id):
            raise ConflictError("Cannot delete a section that is in use")
        self.repository.delete(section)
        self._commit("Cannot delete section")

    def _get_or_404(self, section_id: int) -> Section:
        section = self.repository.get_by_id(section_id)
        if section is None:
            raise NotFoundError("Section not found")
        return section

    def _ensure_parents_exist(self, program_id: int, academic_term_id: int) -> None:
        if self.programs.get_by_id(program_id) is None:
            raise NotFoundError("Program not found")
        if self.terms.get_by_id(academic_term_id) is None:
            raise NotFoundError("Academic term not found")

    def _ensure_unique(
        self,
        program_id: int,
        academic_term_id: int,
        name: str,
        exclude_id: int | None = None,
    ) -> None:
        existing = self.repository.get_by_identity(
            program_id,
            academic_term_id,
            name,
            exclude_id=exclude_id,
        )
        if existing is not None:
            raise ConflictError(
                "A section with this name already exists for the program and term"
            )

    def _commit(self, conflict_message: str) -> None:
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictError(conflict_message)
