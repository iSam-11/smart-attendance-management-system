# Smart Attendance Management System — Project Setup

## 1. Purpose

This document defines the development environment and setup standards for the Smart Attendance Management System.

The project must be reproducible so that:

- A developer can set up the project on a new machine.
- Cursor can understand the project structure.
- Antigravity can work on the project without changing the architecture.
- Backend and frontend can be developed independently.
- Database credentials remain outside source control.

---

# 2. Technology Stack

## Backend

- Python 3.12+
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic
- PyJWT
- Password hashing library
- Pytest

## Database

- Microsoft SQL Server

## Database Driver

Use a SQL Server-compatible Python database driver supported by SQLAlchemy.

The exact driver should be selected during implementation based on the development environment and compatibility.

## Frontend

- HTML5
- CSS3
- Minimal JavaScript

React and Node.js are not required.

## Development Tools

- Git
- GitHub
- Cursor
- Antigravity
- VS Code-compatible editor if required

---

# 3. Required Software

Before implementation, the development machine should have:

1. Python 3.12 or later
2. Microsoft SQL Server
3. Git
4. A code editor
5. Cursor and/or Antigravity

Optional tools:

- SQL Server Management Studio (SSMS)
- Azure Data Studio or another SQL client
- Postman or another API testing client

---

# 4. Python Environment

The backend must use a Python virtual environment.

Recommended structure:

```text
backend/
    .venv/

```

The virtual environment must not be committed to Git.

The application dependencies must be installed inside the virtual environment.

---

# 5. Backend Dependency Categories

The backend will require dependencies for:

## Web Framework

```text
FastAPI
Uvicorn

```

## Validation

```text
Pydantic

```

## Database

```text
SQLAlchemy
SQL Server compatible database driver

```

## Authentication

```text
JWT library
Password hashing library

```

## Testing

```text
Pytest
FastAPI test utilities

```

The exact package versions should be pinned once the initial environment is created.

---

# 6. Backend Project Structure

The initial backend structure should be:

```text
backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── students.py
│   │   ├── faculty.py
│   │   ├── departments.py
│   │   ├── programs.py
│   │   ├── sections.py
│   │   ├── subjects.py
│   │   ├── attendance.py
│   │   ├── corrections.py
│   │   └── reports.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── student.py
│   │   ├── faculty.py
│   │   ├── department.py
│   │   ├── program.py
│   │   ├── section.py
│   │   ├── subject.py
│   │   ├── academic_term.py
│   │   ├── faculty_assignment.py
│   │   ├── student_enrollment.py
│   │   ├── attendance_session.py
│   │   ├── student_attendance.py
│   │   ├── correction_request.py
│   │   └── audit_log.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── student.py
│   │   ├── faculty.py
│   │   ├── attendance.py
│   │   └── correction.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── attendance_service.py
│   │   ├── correction_service.py
│   │   └── report_service.py
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── student_repository.py
│   │   ├── faculty_repository.py
│   │   ├── attendance_repository.py
│   │   └── correction_repository.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── security.py
│   │   └── dependencies.py
│   │
│   └── db/
│       ├── __init__.py
│       ├── database.py
│       └── migrations/
│
├── tests/
│
├── requirements.txt
└── README.md

```

The structure can evolve when implementation reveals a legitimate need.

---

# 7. Frontend Structure

The frontend will initially be simple and framework-free.

```text
frontend/
│
├── index.html
│
├── pages/
│   ├── login.html
│   ├── admin-dashboard.html
│   ├── faculty-dashboard.html
│   ├── student-dashboard.html
│   ├── attendance.html
│   ├── attendance-history.html
│   ├── corrections.html
│   └── reports.html
│
├── css/
│   ├── main.css
│   ├── dashboard.css
│   └── forms.css
│
└── js/
    ├── api.js
    ├── auth.js
    ├── attendance.js
    ├── corrections.js
    └── dashboard.js

```

JavaScript should remain focused on:

- API requests
- Form handling
- Dynamic UI updates
- Authentication token handling
- Table filtering
- Dashboard interactions

Do not introduce a frontend framework unless explicitly approved.

---

# 8. Environment Variables

Sensitive configuration must be stored in environment variables.

Example `.env`:

```text
APP_ENV=development

DATABASE_URL=<database-connection-string>

JWT_SECRET_KEY=<secret>

JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=60

```

The actual `.env` file must never be committed to Git.

---

# 9. Environment Template

The repository should contain:

```text
.env.example

```

Example:

```text
APP_ENV=development

DATABASE_URL=

JWT_SECRET_KEY=

JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=60

```

This file may be committed because it contains no real credentials.

---

# 10. Git Configuration

The repository must contain a `.gitignore`.

At minimum, it should ignore:

```text
.venv/
__pycache__/
*.pyc
.env
.pytest_cache/
.vscode/
.idea/
*.log

```

Do not commit:

- Passwords
- Database credentials
- JWT secrets
- API keys
- Local virtual environments
- Temporary files

---

# 11. Database Configuration

The backend will connect to Microsoft SQL Server through SQLAlchemy.

The database connection must be configurable using environment variables.

The connection information must never be hard-coded inside Python files.

Conceptually:

```text
FastAPI
   ↓
SQLAlchemy
   ↓
SQL Server Driver
   ↓
Microsoft SQL Server

```

---

# 12. Database Migration Strategy

Database schema changes must be version controlled.

The implementation should use a migration tool compatible with SQLAlchemy.

Migration files should be committed to Git.

Example conceptual workflow:

```text
Change SQLAlchemy Model
        ↓
Create Migration
        ↓
Review Migration
        ↓
Apply Migration
        ↓
Update Database

```

Do not manually modify production database schemas without a corresponding migration.

---

# 13. Local Development Workflow

The standard development flow is:

```text
1. Activate virtual environment
        ↓
2. Load environment variables
        ↓
3. Start SQL Server
        ↓
4. Apply database migrations
        ↓
5. Start FastAPI
        ↓
6. Open frontend
        ↓
7. Test functionality

```

The backend should be runnable through Uvicorn.

---

# 14. API Development

FastAPI should expose automatic API documentation.

The development environment should provide:

```text
/docs

```

for Swagger/OpenAPI documentation.

An additional OpenAPI representation should be available where provided by FastAPI.

The API documentation is useful for:

- Development
- Manual API testing
- Debugging
- Understanding endpoints
- Demonstrating the project in interviews

---

# 15. Testing Setup

Testing will be introduced incrementally.

Initial test categories:

## Unit Tests

Test:

- Attendance calculations
- Validation logic
- Permission logic
- Correction rules

## API Tests

Test:

- Login
- Authentication
- Authorization
- Attendance creation
- Attendance retrieval
- Correction submission
- Correction approval/rejection

## Integration Tests

Test interactions between:

```text
FastAPI
   ↓
SQLAlchemy
   ↓
SQL Server

```

Important business workflows should have automated tests.

---

# 16. Development Order

Implementation should follow this order:

```text
1. Project environment
       ↓
2. Database connection
       ↓
3. SQLAlchemy base configuration
       ↓
4. Database migrations
       ↓
5. Core models
       ↓
6. Authentication
       ↓
7. Role-based authorization
       ↓
8. Academic structure
       ↓
9. Faculty assignments
       ↓
10. Student enrollment
       ↓
11. Attendance sessions
       ↓
12. Student attendance
       ↓
13. Correction workflow
       ↓
14. Reports
       ↓
15. Dashboards
       ↓
16. Testing
       ↓
17. Security review
       ↓
18. Deployment

```

Do not build all features simultaneously.

---

# 17. AI Agent Development Rules

Cursor and Antigravity must follow the project documentation.

Before modifying the codebase, they must read:

```text
AGENTS.md
REQUIREMENTS.md
ARCHITECTURE.md
DATABASE.md
PROJECT_SETUP.md

```

Agents must:

- Follow the documented technology stack.
- Use Python for backend development.
- Use FastAPI for APIs.
- Use SQLAlchemy for database access.
- Use Microsoft SQL Server.
- Follow the documented database relationships.
- Keep frontend JavaScript minimal.
- Avoid introducing React or Node.js without approval.
- Avoid unnecessary dependencies.
- Avoid changing database relationships silently.
- Avoid modifying requirements without approval.
- Keep secrets out of source control.
- Write tests for important functionality.
- Explain significant architectural changes before implementation.

---

# 18. Parallel AI Development

Cursor and Antigravity may eventually work on different parts of the project.

They must not simultaneously modify the same architectural area without coordination.

Suggested separation:

```text
Cursor
    ↓
Backend/API development

Antigravity
    ↓
Frontend/UI development

```

This separation may change depending on the actual development workflow.

Shared files require additional care.

---

# 19. Definition of Done

A feature is not considered complete merely because code exists.

A feature should generally include:

- Backend implementation
- Database interaction where required
- Input validation
- Authorization
- Error handling
- Frontend integration where applicable
- Tests for important behavior
- Documentation where appropriate

Example:

Attendance recording is complete only when:

```text
Faculty can authenticate
        ↓
Faculty can access assigned subject
        ↓
Faculty can select section/date
        ↓
Students are loaded
        ↓
Attendance can be marked
        ↓
Validation occurs
        ↓
Records are saved
        ↓
Duplicate records are prevented
        ↓
Audit information is recorded
        ↓
Attendance can be viewed later

```

---

# 20. Deployment Preparation

Deployment will be addressed after the application works locally.

The deployment architecture should eventually support:

```text
Web Client
     ↓
Application Server
     ↓
FastAPI
     ↓
SQL Server

```

Deployment credentials must be provided through environment configuration.

No production credentials should exist in the Git repository.

---

# 21. Project Setup Status

Current status:

**Project Setup Specification — Ready for Implementation**

However, actual installation and project initialization should begin only after the documentation review is complete.

The implementation agent must not change the agreed stack without explicit approval.