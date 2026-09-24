from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.app.api.auth import router as auth_router
from backend.app.api.academic_terms import router as academic_terms_router
from backend.app.api.departments import router as departments_router
from backend.app.api.faculty import router as faculty_router
from backend.app.api.faculty_assignments import router as faculty_assignments_router
from backend.app.api.programs import router as programs_router
from backend.app.api.sections import router as sections_router
from backend.app.api.attendance_sessions import router as attendance_sessions_router
from backend.app.api.student_attendance import router as student_attendance_router
from backend.app.api.correction_requests import router as correction_requests_router
from backend.app.api.reports import router as reports_router
from backend.app.api.audit_logs import router as audit_logs_router
from backend.app.api.students import router as students_router
from backend.app.api.student_enrollments import router as student_enrollments_router
from backend.app.api.subjects import router as subjects_router
from backend.app.core.exceptions import AppError
from backend.app.db.dependencies import get_db

app = FastAPI(
    title="Smart Attendance Management System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
def handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )

app.include_router(auth_router)
app.include_router(departments_router)
app.include_router(academic_terms_router)
app.include_router(programs_router)
app.include_router(sections_router)
app.include_router(students_router)
app.include_router(student_enrollments_router)
app.include_router(faculty_router)
app.include_router(faculty_assignments_router)
app.include_router(subjects_router)
app.include_router(attendance_sessions_router)
app.include_router(student_attendance_router)
app.include_router(correction_requests_router)
app.include_router(reports_router)
app.include_router(audit_logs_router)






@app.get("/")
def root():
    return {
        "message": "Smart Attendance Management System API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/health/db")
def database_health_check(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT DB_NAME()")).scalar()
    return {
        "status": "healthy",
        "database": result,
    }
