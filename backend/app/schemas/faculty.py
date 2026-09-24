from pydantic import BaseModel, ConfigDict, Field, field_validator


class FacultyCreate(BaseModel):
    user_id: int
    department_id: int
    employee_identifier: str = Field(min_length=1, max_length=50)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    is_active: bool = True

    @field_validator("employee_identifier", "first_name")
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


class FacultyUpdate(FacultyCreate):
    pass


class FacultyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    department_id: int
    employee_identifier: str
    first_name: str
    last_name: str | None
    is_active: bool
