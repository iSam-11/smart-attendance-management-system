from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class StudentAttendance(Base):
    __tablename__ = "student_attendance"

    __table_args__ = (
        UniqueConstraint(
            "attendance_session_id",
            "student_id",
            name="uq_student_attendance",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    attendance_session_id: Mapped[int] = mapped_column(
        ForeignKey("attendance_sessions.id"),
        nullable=False,
        index=True,
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    remarks: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    marked_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )