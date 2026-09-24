from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class FacultyAssignment(Base):
    __tablename__ = "faculty_assignments"

    __table_args__ = (
        UniqueConstraint(
            "faculty_id",
            "subject_id",
            "section_id",
            "academic_term_id",
            name="uq_faculty_assignment",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    faculty_id: Mapped[int] = mapped_column(
        ForeignKey("faculty.id"),
        nullable=False,
        index=True,
    )

    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id"),
        nullable=False,
        index=True,
    )

    section_id: Mapped[int] = mapped_column(
        ForeignKey("sections.id"),
        nullable=False,
        index=True,
    )

    academic_term_id: Mapped[int] = mapped_column(
        ForeignKey("academic_terms.id"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )