from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class AcademicTerm(Base):
    __tablename__ = "academic_terms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    semester: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
