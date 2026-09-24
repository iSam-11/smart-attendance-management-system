from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_pagination
from backend.app.core.constants import ROLE_ADMIN, ROLE_FACULTY
from backend.app.core.dependencies import require_role
from backend.app.db.dependencies import get_db
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.student_enrollment import StudentEnrollmentCreate, StudentEnrollmentRead
from backend.app.services.student_enrollment_service import StudentEnrollmentService

router = APIRouter(prefix="/api/student-enrollments", tags=["student-enrollments"])


def get_student_enrollment_service(db: Session = Depends(get_db)) -> StudentEnrollmentService:
    return StudentEnrollmentService(db)


@router.post(
    "",
    response_model=StudentEnrollmentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def create_student_enrollment(
    payload: StudentEnrollmentCreate,
    service: StudentEnrollmentService = Depends(get_student_enrollment_service),
) -> StudentEnrollmentRead:
    return service.create(payload)


@router.get(
    "",
    response_model=PaginatedResponse[StudentEnrollmentRead],
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def list_student_enrollments(
    student_id: int | None = Query(default=None),
    subject_id: int | None = Query(default=None),
    section_id: int | None = Query(default=None),
    academic_term_id: int | None = Query(default=None),
    pagination: PaginationParams = Depends(get_pagination),
    service: StudentEnrollmentService = Depends(get_student_enrollment_service),
) -> PaginatedResponse[StudentEnrollmentRead]:
    return service.list(
        pagination,
        student_id=student_id,
        subject_id=subject_id,
        section_id=section_id,
        academic_term_id=academic_term_id,
    )


@router.get(
    "/{enrollment_id}",
    response_model=StudentEnrollmentRead,
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def get_student_enrollment(
    enrollment_id: int,
    service: StudentEnrollmentService = Depends(get_student_enrollment_service),
) -> StudentEnrollmentRead:
    return service.get(enrollment_id)


@router.delete(
    "/{enrollment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def delete_student_enrollment(
    enrollment_id: int,
    service: StudentEnrollmentService = Depends(get_student_enrollment_service),
) -> None:
    service.delete(enrollment_id)
