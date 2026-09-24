from __future__ import annotations

from datetime import date, time

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.db.models.attendance_session import AttendanceSession


class AttendanceSessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, session_id: int) -> AttendanceSession | None:
        return self.db.get(AttendanceSession, session_id)

    def get_by_unique_composite(
        self,
        faculty_assignment_id: int,
        session_date: date,
        start_time: time,
        exclude_id: int | None = None,
    ) -> AttendanceSession | None:
        stmt = select(AttendanceSession).where(
            AttendanceSession.faculty_assignment_id == faculty_assignment_id,
            AttendanceSession.session_date == session_date,
            AttendanceSession.start_time == start_time,
        )
        if exclude_id is not None:
            stmt = stmt.where(AttendanceSession.id != exclude_id)
        return self.db.scalar(stmt)

    def list(
        self,
        *,
        offset: int,
        limit: int,
        faculty_assignment_id: int | None = None,
        faculty_assignment_ids: list[int] | None = None,
        session_date: date | None = None,
    ) -> list[AttendanceSession]:
        stmt = select(AttendanceSession).order_by(AttendanceSession.id)
        stmt = self._apply_filters(
            stmt,
            faculty_assignment_id=faculty_assignment_id,
            faculty_assignment_ids=faculty_assignment_ids,
            session_date=session_date,
        )
        return list(self.db.scalars(stmt.offset(offset).limit(limit)).all())

    def count(
        self,
        *,
        faculty_assignment_id: int | None = None,
        faculty_assignment_ids: list[int] | None = None,
        session_date: date | None = None,
    ) -> int:
        stmt = select(func.count(AttendanceSession.id))
        stmt = self._apply_filters(
            stmt,
            faculty_assignment_id=faculty_assignment_id,
            faculty_assignment_ids=faculty_assignment_ids,
            session_date=session_date,
        )
        return int(self.db.scalar(stmt) or 0)

    def add(self, session: AttendanceSession) -> AttendanceSession:
        self.db.add(session)
        self.db.flush()
        return session

    def delete(self, session: AttendanceSession) -> None:
        self.db.delete(session)
        self.db.flush()

    def _apply_filters(
        self,
        stmt,
        *,
        faculty_assignment_id: int | None,
        faculty_assignment_ids: list[int] | None,
        session_date: date | None,
    ):
        if faculty_assignment_id is not None:
            stmt = stmt.where(AttendanceSession.faculty_assignment_id == faculty_assignment_id)
        elif faculty_assignment_ids is not None:
            stmt = stmt.where(AttendanceSession.faculty_assignment_id.in_(faculty_assignment_ids))
        if session_date is not None:
            stmt = stmt.where(AttendanceSession.session_date == session_date)
        return stmt
