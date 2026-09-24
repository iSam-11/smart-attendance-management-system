from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AcademicTermCreate(BaseModel):
    academic_year: str = Field(min_length=1, max_length=20)
    semester: str = Field(min_length=1, max_length=30)
    name: str = Field(min_length=1, max_length=100)
    start_date: date
    end_date: date
    is_active: bool = False

    @field_validator("academic_year", "semester", "name")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class AcademicTermUpdate(AcademicTermCreate):
    pass


class AcademicTermRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    academic_year: str
    semester: str
    name: str
    start_date: date
    end_date: date
    is_active: bool
    created_at: datetime
