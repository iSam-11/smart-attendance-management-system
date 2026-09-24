from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProgramCreate(BaseModel):
    department_id: int
    name: str = Field(min_length=1, max_length=150)
    code: str = Field(min_length=1, max_length=30)

    @field_validator("name", "code")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.upper()


class ProgramUpdate(ProgramCreate):
    pass


class ProgramRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    department_id: int
    name: str
    code: str
