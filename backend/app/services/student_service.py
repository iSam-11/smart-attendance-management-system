from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.constants import ROLE_STUDENT
from backend.app.core.exceptions import ConflictError, DomainValidationError, NotFoundError
from backend.app.db.models.student import Student
from backend.app.repositories.department_repository import DepartmentRepository
from backend.app.repositories.program_repository import ProgramRepository
from backend.app.repositories.section_repository import SectionRepository
from backend.app.repositories.student_repository import StudentRepository
from backend.app.repositories.user_repository import get_user_by_id
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.student import StudentCreate, StudentRead, StudentUpdate


class StudentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = StudentRepository(db)
        self.departments = DepartmentRepository(db)
        self.programs = ProgramRepository(db)
        self.sections = SectionRepository(db)

    def create(self, payload: StudentCreate) -> StudentRead:
        self._validate_relations(payload)
        self._ensure_unique(
            payload.user_id,
            payload.student_identifier,
            payload.enrollment_number,
        )
        student = Student(
            user_id=payload.user_id,
            department_id=payload.department_id,
            section_id=payload.section_id,
            student_identifier=payload.student_identifier,
            enrollment_number=payload.enrollment_number,
            first_name=payload.first_name,
            last_name=payload.last_name,
            date_of_birth=payload.date_of_birth,
            admission_year=payload.admission_year,
            is_active=payload.is_active,
        )
        self.repository.add(student)
        self._commit("Student identifier or enrollment number already exists")
        return StudentRead.model_validate(student)

    def get(self, student_id: int) -> StudentRead:
        return StudentRead.model_validate(self._get_or_404(student_id))

    def list(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        department_id: int | None = None,
        section_id: int | None = None,
        is_active: bool | None = None,
    ) -> PaginatedResponse[StudentRead]:
        items = self.repository.list(
            offset=pagination.offset,
            limit=pagination.page_size,
            search=search,
            department_id=department_id,
            section_id=section_id,
            is_active=is_active,
        )
        total = self.repository.count(
            search=search,
            department_id=department_id,
            section_id=section_id,
            is_active=is_active,
        )
        return PaginatedResponse[StudentRead](
            items=[StudentRead.model_validate(item) for item in items],
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
        )

    def update(self, student_id: int, payload: StudentUpdate) -> StudentRead:
        student = self._get_or_404(student_id)
        self._validate_relations(payload)
        self._ensure_unique(
            payload.user_id,
            payload.student_identifier,
            payload.enrollment_number,
            exclude_id=student_id,
        )
        student.user_id = payload.user_id
        student.department_id = payload.department_id
        student.section_id = payload.section_id
        student.student_identifier = payload.student_identifier
        student.enrollment_number = payload.enrollment_number
        student.first_name = payload.first_name
        student.last_name = payload.last_name
        student.date_of_birth = payload.date_of_birth
        student.admission_year = payload.admission_year
        student.is_active = payload.is_active
        self._commit("Student identifier or enrollment number already exists")
        return StudentRead.model_validate(student)

    def _get_or_404(self, student_id: int) -> Student:
        student = self.repository.get_by_id(student_id)
        if student is None:
            raise NotFoundError("Student not found")
        return student

    def _validate_relations(self, payload: StudentCreate) -> None:
        user = get_user_by_id(self.db, payload.user_id)
        if user is None:
            raise NotFoundError("User not found")
        if user.role != ROLE_STUDENT:
            raise DomainValidationError("User must have the STUDENT role")

        if self.departments.get_by_id(payload.department_id) is None:
            raise NotFoundError("Department not found")

        section = self.sections.get_by_id(payload.section_id)
        if section is None:
            raise NotFoundError("Section not found")

        program = self.programs.get_by_id(section.program_id)
        if program is None or program.department_id != payload.department_id:
            raise DomainValidationError(
                "Section does not belong to the selected department"
            )

    def _ensure_unique(
        self,
        user_id: int,
        student_identifier: str,
        enrollment_number: str,
        exclude_id: int | None = None,
    ) -> None:
        if self.repository.get_by_user_id(user_id, exclude_id=exclude_id):
            raise ConflictError("A student profile already exists for this user")
        if self.repository.get_by_student_identifier(
            student_identifier, exclude_id=exclude_id
        ):
            raise ConflictError("Student identifier already exists")
        if self.repository.get_by_enrollment_number(
            enrollment_number, exclude_id=exclude_id
        ):
            raise ConflictError("Enrollment number already exists")

    def _commit(self, conflict_message: str) -> None:
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictError(conflict_message)
