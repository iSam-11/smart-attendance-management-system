from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.db.models.attendance_session import AttendanceSession
from backend.app.db.models.student_attendance import StudentAttendance


class StudentAttendanceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, attendance_id: int) -> StudentAttendance | None:
        return self.db.get(StudentAttendance, attendance_id)

    def get_by_session_and_student(
        self,
        attendance_session_id: int,
        student_id: int,
        exclude_id: int | None = None,
    ) -> StudentAttendance | None:
        stmt = select(StudentAttendance).where(
            StudentAttendance.attendance_session_id == attendance_session_id,
            StudentAttendance.student_id == student_id,
        )
        if exclude_id is not None:
            stmt = stmt.where(StudentAttendance.id != exclude_id)
        return self.db.scalar(stmt)

    def add_all(self, records: list[StudentAttendance]) -> list[StudentAttendance]:
        self.db.add_all(records)
        self.db.flush()
        return records

    def list(
        self,
        *,
        offset: int,
        limit: int,
        attendance_session_id: int | None = None,
        student_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        status: str | None = None,
        session_ids: list[int] | None = None,
    ) -> list[StudentAttendance]:
        stmt = select(StudentAttendance).order_by(StudentAttendance.id)
        stmt = self._apply_filters(
            stmt,
            attendance_session_id=attendance_session_id,
            student_id=student_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
            session_ids=session_ids,
        )
        return list(self.db.scalars(stmt.offset(offset).limit(limit)).all())

    def count(
        self,
        *,
        attendance_session_id: int | None = None,
        student_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        status: str | None = None,
        session_ids: list[int] | None = None,
    ) -> int:
        stmt = select(func.count(StudentAttendance.id))
        stmt = self._apply_filters(
            stmt,
            attendance_session_id=attendance_session_id,
            student_id=student_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
            session_ids=session_ids,
        )
        return int(self.db.scalar(stmt) or 0)

    def _apply_filters(
        self,
        stmt,
        *,
        attendance_session_id: int | None,
        student_id: int | None,
        start_date: date | None,
        end_date: date | None,
        status: str | None,
        session_ids: list[int] | None,
    ):
        if attendance_session_id is not None:
            stmt = stmt.where(StudentAttendance.attendance_session_id == attendance_session_id)
        elif session_ids is not None:
            stmt = stmt.where(StudentAttendance.attendance_session_id.in_(session_ids))

        if student_id is not None:
            stmt = stmt.where(StudentAttendance.student_id == student_id)

        if status is not None:
            stmt = stmt.where(StudentAttendance.status == status)

        if start_date is not None or end_date is not None:
            stmt = stmt.join(
                AttendanceSession,
                StudentAttendance.attendance_session_id == AttendanceSession.id,
            )
            if start_date is not None:
                stmt = stmt.where(AttendanceSession.session_date >= start_date)
            if end_date is not None:
                stmt = stmt.where(AttendanceSession.session_date <= end_date)

        return stmt
