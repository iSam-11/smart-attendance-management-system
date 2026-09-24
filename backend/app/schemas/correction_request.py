from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CorrectionRequestCreate(BaseModel):
    student_attendance_id: int = Field(gt=0)
    requested_status: str = Field(max_length=20)
    reason: str = Field(min_length=1, max_length=500)


class CorrectionRequestReview(BaseModel):
    status: str = Field(max_length=20)
    reviewer_remarks: str | None = Field(default=None, max_length=500)


class CorrectionRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_attendance_id: int
    requested_by: int
    reviewed_by: int | None
    requested_status: str
    reason: str
    request_status: str
    reviewer_remarks: str | None
    created_at: datetime
    reviewed_at: datetime | None
