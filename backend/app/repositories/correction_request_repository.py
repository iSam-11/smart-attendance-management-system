from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.db.models.attendance_session import AttendanceSession
from backend.app.db.models.correction_request import CorrectionRequest
from backend.app.db.models.student_attendance import StudentAttendance


class CorrectionRequestRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, request_id: int) -> CorrectionRequest | None:
        return self.db.get(CorrectionRequest, request_id)

    def get_pending_by_attendance_id(
        self, student_attendance_id: int
    ) -> CorrectionRequest | None:
        stmt = select(CorrectionRequest).where(
            CorrectionRequest.student_attendance_id == student_attendance_id,
            CorrectionRequest.request_status == "PENDING",
        )
        return self.db.scalar(stmt)

    def add(self, request: CorrectionRequest) -> CorrectionRequest:
        self.db.add(request)
        self.db.flush()
        return request

    def list(
        self,
        *,
        offset: int,
        limit: int,
        student_id: int | None = None,
        requested_by_user_id: int | None = None,
        student_attendance_id: int | None = None,
        request_status: str | None = None,
        faculty_assignment_ids: list[int] | None = None,
    ) -> list[CorrectionRequest]:
        stmt = select(CorrectionRequest).order_by(CorrectionRequest.id)
        stmt = self._apply_filters(
            stmt,
            student_id=student_id,
            requested_by_user_id=requested_by_user_id,
            student_attendance_id=student_attendance_id,
            request_status=request_status,
            faculty_assignment_ids=faculty_assignment_ids,
        )
        return list(self.db.scalars(stmt.offset(offset).limit(limit)).all())

    def count(
        self,
        *,
        student_id: int | None = None,
        requested_by_user_id: int | None = None,
        student_attendance_id: int | None = None,
        request_status: str | None = None,
        faculty_assignment_ids: list[int] | None = None,
    ) -> int:
        stmt = select(func.count(CorrectionRequest.id))
        stmt = self._apply_filters(
            stmt,
            student_id=student_id,
            requested_by_user_id=requested_by_user_id,
            student_attendance_id=student_attendance_id,
            request_status=request_status,
            faculty_assignment_ids=faculty_assignment_ids,
        )
        return int(self.db.scalar(stmt) or 0)

    def _apply_filters(
        self,
        stmt,
        *,
        student_id: int | None,
        requested_by_user_id: int | None,
        student_attendance_id: int | None,
        request_status: str | None,
        faculty_assignment_ids: list[int] | None,
    ):
        joined_attendance = False
        joined_session = False

        if requested_by_user_id is not None:
            stmt = stmt.where(CorrectionRequest.requested_by == requested_by_user_id)

        if student_attendance_id is not None:
            stmt = stmt.where(CorrectionRequest.student_attendance_id == student_attendance_id)

        if request_status is not None:
            stmt = stmt.where(CorrectionRequest.request_status == request_status)

        if faculty_assignment_ids is not None:
            if not joined_attendance:
                stmt = stmt.join(
                    StudentAttendance,
                    CorrectionRequest.student_attendance_id == StudentAttendance.id,
                )
                joined_attendance = True
            if not joined_session:
                stmt = stmt.join(
                    AttendanceSession,
                    StudentAttendance.attendance_session_id == AttendanceSession.id,
                )
                joined_session = True
            stmt = stmt.where(AttendanceSession.faculty_assignment_id.in_(faculty_assignment_ids))

        if student_id is not None:
            if not joined_attendance:
                stmt = stmt.join(
                    StudentAttendance,
                    CorrectionRequest.student_attendance_id == StudentAttendance.id,
                )
                joined_attendance = True
            stmt = stmt.where(StudentAttendance.student_id == student_id)

        return stmt
