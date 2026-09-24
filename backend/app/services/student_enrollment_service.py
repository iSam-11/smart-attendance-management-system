from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.exceptions import ConflictError, DomainValidationError, NotFoundError
from backend.app.db.models.student_enrollment import StudentEnrollment
from backend.app.repositories.academic_term_repository import AcademicTermRepository
from backend.app.repositories.section_repository import SectionRepository
from backend.app.repositories.student_enrollment_repository import StudentEnrollmentRepository
from backend.app.repositories.student_repository import StudentRepository
from backend.app.repositories.subject_repository import SubjectRepository
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.student_enrollment import StudentEnrollmentCreate, StudentEnrollmentRead


class StudentEnrollmentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = StudentEnrollmentRepository(db)
        self.students = StudentRepository(db)
        self.subjects = SubjectRepository(db)
        self.sections = SectionRepository(db)
        self.academic_terms = AcademicTermRepository(db)

    def create(self, payload: StudentEnrollmentCreate) -> StudentEnrollmentRead:
        self._validate_relations(payload)
        self._ensure_unique(
            payload.student_id,
            payload.subject_id,
            payload.section_id,
            payload.academic_term_id,
        )

        enrollment = StudentEnrollment(
            student_id=payload.student_id,
            subject_id=payload.subject_id,
            section_id=payload.section_id,
            academic_term_id=payload.academic_term_id,
        )
        self.repository.add(enrollment)
        self._commit("Student is already enrolled in this subject for the section and term")
        return StudentEnrollmentRead.model_validate(enrollment)

    def get(self, enrollment_id: int) -> StudentEnrollmentRead:
        return StudentEnrollmentRead.model_validate(self._get_or_404(enrollment_id))

    def list(
        self,
        pagination: PaginationParams,
        student_id: int | None = None,
        subject_id: int | None = None,
        section_id: int | None = None,
        academic_term_id: int | None = None,
    ) -> PaginatedResponse[StudentEnrollmentRead]:
        items = self.repository.list(
            offset=pagination.offset,
            limit=pagination.page_size,
            student_id=student_id,
            subject_id=subject_id,
            section_id=section_id,
            academic_term_id=academic_term_id,
        )
        total = self.repository.count(
            student_id=student_id,
            subject_id=subject_id,
            section_id=section_id,
            academic_term_id=academic_term_id,
        )
        return PaginatedResponse[StudentEnrollmentRead](
            items=[StudentEnrollmentRead.model_validate(item) for item in items],
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
        )

    def delete(self, enrollment_id: int) -> None:
        enrollment = self._get_or_404(enrollment_id)
        self.repository.delete(enrollment)
        self.db.commit()

    def _get_or_404(self, enrollment_id: int) -> StudentEnrollment:
        enrollment = self.repository.get_by_id(enrollment_id)
        if enrollment is None:
            raise NotFoundError("Student enrollment not found")
        return enrollment

    def _validate_relations(self, payload: StudentEnrollmentCreate) -> None:
        student = self.students.get_by_id(payload.student_id)
        if student is None:
            raise NotFoundError("Student not found")
        if not student.is_active:
            raise DomainValidationError("Student is not active")

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

        if student.section_id != payload.section_id:
            raise DomainValidationError("Student's section is not compatible with the enrollment section")

    def _ensure_unique(
        self,
        student_id: int,
        subject_id: int,
        section_id: int,
        academic_term_id: int,
        exclude_id: int | None = None,
    ) -> None:
        if self.repository.get_by_unique_composite(
            student_id,
            subject_id,
            section_id,
            academic_term_id,
            exclude_id=exclude_id,
        ):
            raise ConflictError("Student is already enrolled in this subject for the section and term")

    def _commit(self, conflict_message: str) -> None:
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictError(conflict_message)
