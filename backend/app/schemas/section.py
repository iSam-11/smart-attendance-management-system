from pydantic import BaseModel, ConfigDict, Field, field_validator


class SectionCreate(BaseModel):
    program_id: int
    academic_term_id: int
    name: str = Field(min_length=1, max_length=50)

    @field_validator("name")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value


class SectionUpdate(SectionCreate):
    pass


class SectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    program_id: int
    academic_term_id: int
    name: str
