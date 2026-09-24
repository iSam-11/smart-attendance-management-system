from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class StudentAttendanceReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: int
    student_name: str
    enrollment_number: str
    subject_id: int
    subject_name: str
    subject_code: str
    section_id: int
    section_name: str
    academic_term_id: int
    total_conducted_classes: int
    present_classes: int
    absent_classes: int
    attendance_percentage: float


class SubjectAttendanceReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: int
    student_name: str
    enrollment_number: str
    subject_id: int
    subject_name: str
    subject_code: str
    section_id: int
    section_name: str
    academic_term_id: int
    total_conducted_classes: int
    present_classes: int
    absent_classes: int
    attendance_percentage: float


class SectionAttendanceReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: int
    student_name: str
    enrollment_number: str
    section_id: int
    section_name: str
    subject_id: int
    subject_name: str
    subject_code: str
    academic_term_id: int
    total_conducted_classes: int
    present_classes: int
    absent_classes: int
    attendance_percentage: float


class LowAttendanceReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: int
    student_name: str
    enrollment_number: str
    section_id: int
    section_name: str
    subject_id: int
    subject_name: str
    subject_code: str
    academic_term_id: int
    total_conducted_classes: int
    present_classes: int
    absent_classes: int
    attendance_percentage: float
    threshold: float
