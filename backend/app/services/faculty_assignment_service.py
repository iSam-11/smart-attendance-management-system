from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.exceptions import ConflictError, DomainValidationError, NotFoundError
from backend.app.db.models.faculty_assignment import FacultyAssignment
from backend.app.repositories.academic_term_repository import AcademicTermRepository
from backend.app.repositories.faculty_assignment_repository import FacultyAssignmentRepository
from backend.app.repositories.faculty_repository import FacultyRepository
from backend.app.repositories.program_repository import ProgramRepository
from backend.app.repositories.section_repository import SectionRepository
from backend.app.repositories.subject_repository import SubjectRepository
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.faculty_assignment import (
    FacultyAssignmentCreate,
    FacultyAssignmentRead,
    FacultyAssignmentUpdate,
)


class FacultyAssignmentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = FacultyAssignmentRepository(db)
        self.faculty = FacultyRepository(db)
        self.subjects = SubjectRepository(db)
        self.sections = SectionRepository(db)
        self.programs = ProgramRepository(db)
        self.academic_terms = AcademicTermRepository(db)

    def create(self, payload: FacultyAssignmentCreate) -> FacultyAssignmentRead:
        self._validate_relations(payload)
        self._ensure_unique(
            payload.faculty_id,
            payload.subject_id,
            payload.section_id,
            payload.academic_term_id,
        )

        assignment = FacultyAssignment(
            faculty_id=payload.faculty_id,
            subject_id=payload.subject_id,
            section_id=payload.section_id,
            academic_term_id=payload.academic_term_id,
        )
        self.repository.add(assignment)
        self._commit("Faculty assignment already exists for this subject, section, and term")
        return FacultyAssignmentRead.model_validate(assignment)

    def get(self, assignment_id: int) -> FacultyAssignmentRead:
        return FacultyAssignmentRead.model_validate(self._get_or_404(assignment_id))

    def list(
        self,
        pagination: PaginationParams,
        faculty_id: int | None = None,
        subject_id: int | None = None,
        section_id: int | None = None,
        academic_term_id: int | None = None,
    ) -> PaginatedResponse[FacultyAssignmentRead]:
        items = self.repository.list(
            offset=pagination.offset,
            limit=pagination.page_size,
            faculty_id=faculty_id,
            subject_id=subject_id,
            section_id=section_id,
            academic_term_id=academic_term_id,
        )
        total = self.repository.count(
            faculty_id=faculty_id,
            subject_id=subject_id,
            section_id=section_id,
            academic_term_id=academic_term_id,
        )
        return PaginatedResponse[FacultyAssignmentRead](
            items=[FacultyAssignmentRead.model_validate(item) for item in items],
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
        )

    def update(
        self, assignment_id: int, payload: FacultyAssignmentUpdate
    ) -> FacultyAssignmentRead:
        assignment = self._get_or_404(assignment_id)
        self._validate_relations(payload)
        self._ensure_unique(
            payload.faculty_id,
            payload.subject_id,
            payload.section_id,
            payload.academic_term_id,
            exclude_id=assignment_id,
        )

        assignment.faculty_id = payload.faculty_id
        assignment.subject_id = payload.subject_id
        assignment.section_id = payload.section_id
        assignment.academic_term_id = payload.academic_term_id

        self._commit("Faculty assignment already exists for this subject, section, and term")
        return FacultyAssignmentRead.model_validate(assignment)

    def delete(self, assignment_id: int) -> None:
        assignment = self._get_or_404(assignment_id)
        if self.repository.is_in_use(assignment_id):
            raise DomainValidationError(
                "Cannot delete faculty assignment because attendance sessions exist for it"
            )
        self.repository.delete(assignment)
        self.db.commit()

    def _get_or_404(self, assignment_id: int) -> FacultyAssignment:
        assignment = self.repository.get_by_id(assignment_id)
        if assignment is None:
            raise NotFoundError("Faculty assignment not found")
        return assignment

    def _validate_relations(self, payload: FacultyAssignmentCreate) -> None:
        faculty = self.faculty.get_by_id(payload.faculty_id)
        if faculty is None:
            raise NotFoundError("Faculty not found")
        if not faculty.is_active:
            raise DomainValidationError("Faculty is not active")

        subject = self.subjects.get_by_id(payload.subject_id)
        if subject is None:
            raise NotFoundError("Subject not found")
        if not subject.is_active:
            raise DomainValidationError("Subject is not active")

        section = self.sections.get_by_id(payload.section_id)
        if section is None:
            raise NotFoundError("Section not found")

        term = self.academic_terms.get_by_id(payload.academic_term_id)
        if term is None:
            raise NotFoundError("Academic term not found")
        if not term.is_active:
            raise DomainValidationError("Academic term is not active")

        if section.academic_term_id != payload.academic_term_id:
            raise DomainValidationError("Section does not belong to the selected academic term")

        program = self.programs.get_by_id(section.program_id)
        if program is None or program.department_id != subject.department_id:
            raise DomainValidationError("Subject does not belong to the section's department")

        if faculty.department_id != subject.department_id:
            raise DomainValidationError("Faculty does not belong to the subject's department")

    def _ensure_unique(
        self,
        faculty_id: int,
        subject_id: int,
        section_id: int,
        academic_term_id: int,
        exclude_id: int | None = None,
    ) -> None:
        if self.repository.get_by_unique_composite(
            faculty_id,
            subject_id,
            section_id,
            academic_term_id,
            exclude_id=exclude_id,
        ):
            raise ConflictError(
                "Faculty assignment already exists for this subject, section, and term"
            )

    def _commit(self, conflict_message: str) -> None:
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictError(conflict_message)
