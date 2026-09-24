from __future__ import annotations

from datetime import date, datetime
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.constants import ROLE_ADMIN, ROLE_FACULTY
from backend.app.core.exceptions import ConflictError, DomainValidationError, NotFoundError
from backend.app.db.models.attendance_session import AttendanceSession
from backend.app.db.models.audit_log import AuditLog
from backend.app.repositories.academic_term_repository import AcademicTermRepository
from backend.app.repositories.attendance_session_repository import AttendanceSessionRepository
from backend.app.repositories.faculty_assignment_repository import FacultyAssignmentRepository
from backend.app.repositories.faculty_repository import FacultyRepository
from backend.app.repositories.section_repository import SectionRepository
from backend.app.repositories.subject_repository import SubjectRepository
from backend.app.schemas.attendance_session import (
    AttendanceSessionCreate,
    AttendanceSessionRead,
    AttendanceSessionUpdate,
)
from backend.app.schemas.common import PaginatedResponse, PaginationParams


class AttendanceSessionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AttendanceSessionRepository(db)
        self.assignment_repo = FacultyAssignmentRepository(db)
        self.faculty_repo = FacultyRepository(db)
        self.subject_repo = SubjectRepository(db)
        self.section_repo = SectionRepository(db)
        self.term_repo = AcademicTermRepository(db)

    def create(
        self, payload: AttendanceSessionCreate, current_user: dict
    ) -> AttendanceSessionRead:
        role = current_user.get("role")
        user_id = int(current_user.get("sub", 0))

        assignment = self.assignment_repo.get_by_id(payload.faculty_assignment_id)
        if assignment is None:
            raise NotFoundError("Faculty assignment not found")

        if role == ROLE_FACULTY:
            faculty = self.faculty_repo.get_by_user_id(user_id)
            if faculty is None or assignment.faculty_id != faculty.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Faculty cannot create attendance session for another faculty's assignment",
                )
        elif role != ROLE_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        self._validate_assignment_active(assignment)

        if payload.end_time is not None and payload.end_time <= payload.start_time:
            raise DomainValidationError("end_time must be later than start_time")

        self._ensure_unique(
            payload.faculty_assignment_id,
            payload.session_date,
            payload.start_time,
        )

        session = AttendanceSession(
            faculty_assignment_id=payload.faculty_assignment_id,
            session_date=payload.session_date,
            start_time=payload.start_time,
            end_time=payload.end_time,
            topic=payload.topic,
            status=payload.status or "OPEN",
        )
        self.repository.add(session)

        now = datetime.utcnow()
        try:
            self.db.flush()
            audit_log = AuditLog(
                user_id=user_id,
                action="SESSION_CREATED",
                entity_type="AttendanceSession",
                entity_id=session.id,
                new_values=f"Created session for assignment {payload.faculty_assignment_id} on {payload.session_date}",
                created_at=now,
            )
            self.db.add(audit_log)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictError("Attendance session already exists for this assignment, date, and start time")
        except Exception:
            self.db.rollback()
            raise

        return AttendanceSessionRead.model_validate(session)

    def get(self, session_id: int, current_user: dict) -> AttendanceSessionRead:
        session = self._get_or_404(session_id)
        self._authorize_access(session, current_user)
        return AttendanceSessionRead.model_validate(session)

    def list(
        self,
        pagination: PaginationParams,
        current_user: dict,
        faculty_assignment_id: int | None = None,
        session_date: date | None = None,
    ) -> PaginatedResponse[AttendanceSessionRead]:
        role = current_user.get("role")
        user_id = int(current_user.get("sub", 0))

        if role == ROLE_ADMIN:
            items = self.repository.list(
                offset=pagination.offset,
                limit=pagination.page_size,
                faculty_assignment_id=faculty_assignment_id,
                session_date=session_date,
            )
            total = self.repository.count(
                faculty_assignment_id=faculty_assignment_id,
                session_date=session_date,
            )
        elif role == ROLE_FACULTY:
            faculty = self.faculty_repo.get_by_user_id(user_id)
            if faculty is None:
                return PaginatedResponse[AttendanceSessionRead](
                    items=[], page=pagination.page, page_size=pagination.page_size, total=0
                )

            my_assignments = self.assignment_repo.list(
                offset=0, limit=1000, faculty_id=faculty.id
            )
            my_assignment_ids = [a.id for a in my_assignments]

            if faculty_assignment_id is not None:
                if faculty_assignment_id not in my_assignment_ids:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Insufficient permissions",
                    )
                target_ids = [faculty_assignment_id]
            else:
                target_ids = my_assignment_ids

            if not target_ids:
                return PaginatedResponse[AttendanceSessionRead](
                    items=[], page=pagination.page, page_size=pagination.page_size, total=0
                )

            items = self.repository.list(
                offset=pagination.offset,
                limit=pagination.page_size,
                faculty_assignment_ids=target_ids,
                session_date=session_date,
            )
            total = self.repository.count(
                faculty_assignment_ids=target_ids,
                session_date=session_date,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return PaginatedResponse[AttendanceSessionRead](
            items=[AttendanceSessionRead.model_validate(item) for item in items],
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
        )

    def update(
        self,
        session_id: int,
        payload: AttendanceSessionUpdate,
        current_user: dict,
    ) -> AttendanceSessionRead:
        session = self._get_or_404(session_id)
        self._authorize_access(session, current_user)

        if payload.end_time is not None and payload.end_time <= payload.start_time:
            raise DomainValidationError("end_time must be later than start_time")

        self._ensure_unique(
            session.faculty_assignment_id,
            payload.session_date,
            payload.start_time,
            exclude_id=session_id,
        )

        session.session_date = payload.session_date
        session.start_time = payload.start_time
        session.end_time = payload.end_time
        session.topic = payload.topic
        session.status = payload.status

        self._commit("Attendance session already exists for this assignment, date, and start time")
        return AttendanceSessionRead.model_validate(session)

    def _get_or_404(self, session_id: int) -> AttendanceSession:
        session = self.repository.get_by_id(session_id)
        if session is None:
            raise NotFoundError("Attendance session not found")
        return session

    def _authorize_access(self, session: AttendanceSession, current_user: dict) -> None:
        role = current_user.get("role")
        user_id = int(current_user.get("sub", 0))

        if role == ROLE_ADMIN:
            return
        elif role == ROLE_FACULTY:
            faculty = self.faculty_repo.get_by_user_id(user_id)
            assignment = self.assignment_repo.get_by_id(session.faculty_assignment_id)
            if faculty is None or assignment is None or assignment.faculty_id != faculty.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

    def _validate_assignment_active(self, assignment) -> None:
        faculty = self.faculty_repo.get_by_id(assignment.faculty_id)
        if faculty is None or not faculty.is_active:
            raise DomainValidationError("Faculty is not active")

        subject = self.subject_repo.get_by_id(assignment.subject_id)
        if subject is None or not subject.is_active:
            raise DomainValidationError("Subject is not active")

        term = self.term_repo.get_by_id(assignment.academic_term_id)
        if term is None or not term.is_active:
            raise DomainValidationError("Academic term is not active")

        section = self.section_repo.get_by_id(assignment.section_id)
        if section is None:
            raise DomainValidationError("Section not found")

    def _ensure_unique(
        self,
        faculty_assignment_id: int,
        session_date: date,
        start_time: time,
        exclude_id: int | None = None,
    ) -> None:
        existing = self.repository.get_by_unique_composite(
            faculty_assignment_id,
            session_date,
            start_time,
            exclude_id=exclude_id,
        )
        if existing is not None:
            raise ConflictError(
                "Attendance session already exists for this assignment, date, and start time"
            )

    def _commit(self, conflict_message: str) -> None:
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictError(conflict_message)
