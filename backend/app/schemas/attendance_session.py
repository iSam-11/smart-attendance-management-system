from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field


class AttendanceSessionCreate(BaseModel):
    faculty_assignment_id: int = Field(gt=0)
    session_date: date
    start_time: time
    end_time: time | None = None
    topic: str | None = Field(default=None, max_length=255)
    status: str = Field(default="OPEN", max_length=30)


class AttendanceSessionUpdate(BaseModel):
    session_date: date
    start_time: time
    end_time: time | None = None
    topic: str | None = Field(default=None, max_length=255)
    status: str = Field(default="OPEN", max_length=30)


class AttendanceSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    faculty_assignment_id: int
    session_date: date
    start_time: time
    end_time: time | None
    topic: str | None
    status: str
    created_at: datetime
