from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StudentAttendanceEntry(BaseModel):
    student_id: int = Field(gt=0)
    status: str = Field(max_length=20)
    remarks: str | None = Field(default=None, max_length=255)


class StudentAttendanceBulkCreate(BaseModel):
    attendance_session_id: int = Field(gt=0)
    entries: list[StudentAttendanceEntry] = Field(min_items=1)


class StudentAttendanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    attendance_session_id: int
    student_id: int
    status: str
    remarks: str | None
    marked_at: datetime
