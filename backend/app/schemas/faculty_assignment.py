from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FacultyAssignmentCreate(BaseModel):
    faculty_id: int = Field(gt=0)
    subject_id: int = Field(gt=0)
    section_id: int = Field(gt=0)
    academic_term_id: int = Field(gt=0)


class FacultyAssignmentUpdate(FacultyAssignmentCreate):
    pass


class FacultyAssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    faculty_id: int
    subject_id: int
    section_id: int
    academic_term_id: int
    created_at: datetime
