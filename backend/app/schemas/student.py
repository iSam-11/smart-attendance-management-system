from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StudentCreate(BaseModel):
    user_id: int
    department_id: int
    section_id: int
    student_identifier: str = Field(min_length=1, max_length=50)
    enrollment_number: str = Field(min_length=1, max_length=50)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    date_of_birth: date | None = None
    admission_year: int = Field(ge=1990, le=2100)
    is_active: bool = True

    @field_validator("student_identifier", "enrollment_number", "first_name")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("last_name")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class StudentUpdate(StudentCreate):
    pass


class StudentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    department_id: int
    section_id: int
    student_identifier: str
    enrollment_number: str
    first_name: str
    last_name: str | None
    date_of_birth: date | None
    admission_year: int
    is_active: bool
