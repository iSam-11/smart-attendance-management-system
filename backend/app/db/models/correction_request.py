from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class CorrectionRequest(Base):
    __tablename__ = "correction_requests"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    student_attendance_id: Mapped[int] = mapped_column(
        ForeignKey("student_attendance.id"),
        nullable=False,
        index=True,
    )

    requested_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    reviewed_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    requested_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    request_status: Mapped[str] = mapped_column(
        String(20),
        default="PENDING",
        nullable=False,
    )

    reviewer_remarks: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )