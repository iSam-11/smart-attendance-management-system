from pydantic import BaseModel, ConfigDict, Field, field_validator


class SubjectCreate(BaseModel):
    department_id: int
    subject_code: str = Field(min_length=1, max_length=30)
    name: str = Field(min_length=1, max_length=150)
    credits: int = Field(ge=1, le=50)
    is_active: bool = True

    @field_validator("subject_code", "name")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("subject_code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.upper()


class SubjectUpdate(SubjectCreate):
    pass


class SubjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    department_id: int
    subject_code: str
    name: str
    credits: int
    is_active: bool
