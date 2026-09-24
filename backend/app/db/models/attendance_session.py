from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    __table_args__ = (
        UniqueConstraint(
            "faculty_assignment_id",
            "session_date",
            "start_time",
            name="uq_attendance_session",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    faculty_assignment_id: Mapped[int] = mapped_column(
        ForeignKey("faculty_assignments.id"),
        nullable=False,
        index=True,
    )

    session_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    end_time: Mapped[time | None] = mapped_column(
        Time,
        nullable=True,
    )

    topic: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="OPEN",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )