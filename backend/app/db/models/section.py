from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class Section(Base):
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    program_id: Mapped[int] = mapped_column(
        ForeignKey("programs.id"),
        nullable=False,
        index=True,
    )
    academic_term_id: Mapped[int] = mapped_column(
        ForeignKey("academic_terms.id"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
