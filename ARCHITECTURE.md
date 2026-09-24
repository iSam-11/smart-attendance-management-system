# Smart Attendance Management System — Architecture

## 1. Architecture Objective

The Smart Attendance Management System is a web-based application designed to manage attendance for a college with approximately:

- 5,000 students
- 200 faculty members
- Multiple departments
- Multiple programs/classes
- Multiple sections
- Multiple subjects

The architecture must support:

- Role-based authentication and authorization
- Attendance recording
- Attendance history
- Attendance correction requests
- Correction review and approval
- Low-attendance identification
- Dashboards
- Reports
- Data integrity
- Auditability
- Future scalability

The system should remain understandable and maintainable for a Python-focused developer.

---

# 2. Technology Stack

## Frontend

- HTML5
- CSS3
- Minimal JavaScript

React is not required for the initial implementation.

JavaScript should only be used where dynamic browser-side behavior is required.

## Backend

- Python
- FastAPI

FastAPI will provide:

- REST APIs
- Request validation
- Response validation
- Authentication endpoints
- Business logic endpoints
- Automatic OpenAPI/Swagger documentation

## Database

- Microsoft SQL Server

SQL Server will be the primary persistent database.

## ORM

- SQLAlchemy

SQLAlchemy will provide:

- Database models
- Relationships
- Query abstraction
- Transaction management
- Database interaction from Python

## Authentication

- JWT-based authentication
- Secure password hashing
- Role-based authorization

## Testing

- Pytest
- FastAPI test client/API testing

## Version Control

- Git
- GitHub

---

# 3. High-Level Architecture

```text
┌──────────────────────────────────────┐
│             Web Browser              │
│                                      │
│          HTML + CSS + JS             │
└──────────────────┬───────────────────┘
                   │
                   │ HTTP / REST API
                   ▼
┌──────────────────────────────────────┐
│             FastAPI                  │
│                                      │
│  ┌────────────┐  ┌────────────────┐ │
│  │ Auth APIs  │  │ Attendance APIs│ │
│  └────────────┘  └────────────────┘ │
│                                      │
│  ┌────────────┐  ┌────────────────┐ │
│  │ User APIs  │  │ Report APIs    │ │
│  └────────────┘  └────────────────┘ │
│                                      │
│          Business Logic              │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│             SQLAlchemy               │
│              ORM Layer               │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│        Microsoft SQL Server          │
│                                      │
│ Users                                │
│ Students                             │
│ Faculty                              │
│ Departments                          │
│ Programs                             │
│ Sections                             │
│ Subjects                             │
│ Enrollments                          │
│ Attendance                           │
│ Correction Requests                  │
│ Audit Logs                           │
└──────────────────────────────────────┘

```

---

# 4. Architectural Layers

The backend will follow a layered architecture.

```text
API / Routes
     ↓
Services / Business Logic
     ↓
Repositories / Database Access
     ↓
SQLAlchemy Models
     ↓
Microsoft SQL Server

```

## 4.1 API Layer

Responsible for:

- Receiving HTTP requests
- Validating request data
- Authentication checks
- Authorization checks
- Calling service functions
- Returning API responses

The API layer should not contain complex business logic.

## 4.2 Service Layer

Responsible for:

- Attendance business rules
- Attendance percentage calculations
- Correction workflows
- Permission-sensitive operations
- Report generation logic
- Other application rules

Business logic should primarily live here.

## 4.3 Repository/Data Access Layer

Responsible for:

- Database queries
- Creating records
- Updating records
- Fetching records
- Deleting records where permitted

Database access should not be scattered throughout API route files.

## 4.4 Model Layer

SQLAlchemy models will represent the database entities and relationships.

---

# 5. Core Roles

The initial system will contain three primary roles.

## 5.1 Admin

Admin can:

- Manage users
- Manage students
- Manage faculty
- Manage departments
- Manage programs/classes
- Manage sections
- Manage subjects
- Assign faculty
- View institution-level attendance information
- View reports
- Review system activity

## 5.2 Faculty

Faculty can:

- View assigned subjects
- View assigned sections
- Record attendance
- Edit attendance according to allowed rules
- View attendance history
- Review correction requests
- Approve/reject correction requests
- View attendance reports
- Identify low-attendance students

## 5.3 Student

Student can:

- Log in
- View personal attendance
- View attendance history
- View attendance percentage
- View subject-wise attendance
- Submit attendance correction requests
- Track correction request status

Users must only access data permitted by their role and assignments.

---

# 6. Database Entities

The initial database design will contain the following major entities.

## 6.1 User

Stores authentication and account information.

Important fields:

- id
- username/email
- password_hash
- role
- is_active
- created_at
- updated_at

Passwords must never be stored in plain text.

---

## 6.2 Student

Stores student-specific information.

Important fields:

- id
- user_id
- student_identifier
- first_name
- last_name
- department_id
- program_id
- section_id
- admission_year
- is_active

---

## 6.3 Faculty

Stores faculty-specific information.

Important fields:

- id
- user_id
- employee_identifier
- first_name
- last_name
- department_id
- is_active

---

## 6.4 Department

Stores department information.

Important fields:

- id
- name
- code
- is_active

Example:

```text
Computer Science and Engineering
Information Technology
Electronics and Communication

```

---

## 6.5 Program

Represents an academic program/class.

Important fields:

- id
- department_id
- name
- code
- duration
- is_active

---

## 6.6 Section

Represents a class section.

Important fields:

- id
- program_id
- name
- academic_year
- semester
- is_active

Example:

```text
CSE
2026
Semester 5
Section A

```

---

## 6.7 Subject

Stores subject information.

Important fields:

- id
- subject_code
- name
- credits
- department_id
- is_active

---

## 6.8 Faculty Assignment

Represents which faculty member teaches which subject to which section.

Important fields:

- id
- faculty_id
- subject_id
- section_id
- academic_year
- semester
- is_active

This prevents attendance permissions from being based only on the user's role.

A faculty member should normally be able to record attendance only for subjects/sections assigned to them.

---

## 6.9 Student Enrollment

Represents the relationship between students and academic sections/subjects.

Important fields:

- id
- student_id
- section_id
- subject_id
- academic_year
- semester
- is_active

---

## 6.10 Attendance

Stores individual attendance records.

Important fields:

- id
- student_id
- subject_id
- section_id
- faculty_id
- attendance_date
- status
- marked_at
- updated_at

Possible attendance statuses:

```text
PRESENT
ABSENT

```

The design should allow future statuses if required.

---

## 6.11 Correction Request

Stores requests made when a student believes an attendance record is incorrect.

Important fields:

- id
- attendance_id
- student_id
- reason
- requested_status
- status
- reviewed_by
- review_comment
- created_at
- reviewed_at

Possible request statuses:

```text
PENDING
APPROVED
REJECTED

```

---

## 6.12 Audit Log

Stores important system actions.

Important fields:

- id
- user_id
- action
- entity_type
- entity_id
- description
- created_at

Examples:

```text
Attendance created
Attendance modified
Correction requested
Correction approved
Correction rejected
User created

```

---

# 7. Entity Relationship Overview

```text
Department
   │
   ├─────────────── Faculty
   │
   ├─────────────── Student
   │
   ├─────────────── Program
   │                      │
   │                      └──── Section
   │                               │
   │                               └──── Students
   │
   └─────────────── Subject
                            │
                            └──── Faculty Assignment
                                      │
                                      ├── Faculty
                                      ├── Subject
                                      └── Section

Student
   │
   └──── Enrollment
             │
             └──── Subject

Student
   │
   └──── Attendance
             │
             └──── Correction Request

User
   │
   ├──── Student
   └──── Faculty

User
   │
   └──── Audit Log

```

---

# 8. Attendance Workflow

## 8.1 Recording Attendance

```text
Faculty Login
      ↓
Authentication
      ↓
Authorization
      ↓
View Assigned Subjects
      ↓
Select Subject
      ↓
Select Section
      ↓
Select Date
      ↓
Load Enrolled Students
      ↓
Mark Present / Absent
      ↓
Validate Attendance
      ↓
Save Records
      ↓
Create Audit Entry

```

## 8.2 Attendance Validation

The system should validate:

- Faculty is authenticated
- Faculty has permission for the subject/section
- Student belongs to the relevant section
- Student is enrolled
- Attendance date is valid
- Duplicate attendance records are prevented
- Required fields are present

---

# 9. Attendance Correction Workflow

```text
Student
   ↓
Views Attendance
   ↓
Selects Incorrect Record
   ↓
Provides Reason
   ↓
Submits Correction Request
   ↓
PENDING
   ↓
Faculty Reviews
   ├───────────────┐
   ▼               ▼
APPROVED         REJECTED
   │
   ▼
Attendance Updated
   │
   ▼
Audit Log Created

```

Correction requests must not directly modify attendance without authorization.

---

# 10. Low Attendance Calculation

The system will calculate attendance percentage using:

```text
Attendance Percentage =
(Present Classes / Total Conducted Classes) × 100

```

Example:

```text
Present = 18
Total = 24

Attendance = (18 / 24) × 100
           = 75%

```

The threshold should be configurable rather than hard-coded wherever practical.

The system should support:

- Overall attendance
- Subject-wise attendance
- Section-level summaries
- Low-attendance student lists

---

# 11. Authentication Architecture

Authentication flow:

```text
User
 ↓
Login
 ↓
FastAPI Authentication Endpoint
 ↓
Verify Credentials
 ↓
Password Hash Verification
 ↓
Generate JWT
 ↓
Return Token
 ↓
Client Uses Token
 ↓
Protected API
 ↓
Authentication + Authorization
 ↓
Request Processed

```

Security requirements:

- Passwords must be hashed.
- Passwords must never be stored in plain text.
- Protected endpoints must require authentication.
- Role permissions must be enforced server-side.
- Sensitive operations must be logged.

---

# 12. API Design

The application will expose REST-style APIs.

Example API groups:

```text
/api/auth
/api/users
/api/students
/api/faculty
/api/departments
/api/programs
/api/sections
/api/subjects
/api/enrollments
/api/assignments
/api/attendance
/api/corrections
/api/reports
/api/audit-logs

```

Example endpoints:

```text
POST   /api/auth/login

GET    /api/students
GET    /api/students/{id}

POST   /api/attendance
GET    /api/attendance/student/{student_id}

POST   /api/corrections
GET    /api/corrections
PUT    /api/corrections/{id}/review

GET    /api/reports/attendance
GET    /api/reports/low-attendance

```

Exact endpoints may evolve during implementation, but API design should remain consistent and REST-oriented.

---

# 13. Frontend Architecture

The frontend will initially use:

- HTML
- CSS
- Minimal JavaScript

The frontend will communicate with FastAPI using HTTP requests.

Example:

```text
Browser
   │
   │ GET /api/attendance
   ▼
FastAPI
   │
   ▼
Service Layer
   │
   ▼
SQLAlchemy
   │
   ▼
SQL Server

```

The frontend should contain role-specific dashboards.

## Admin Dashboard

Potential sections:

- Total students
- Total faculty
- Departments
- Attendance overview
- Low-attendance students
- User management
- Reports

## Faculty Dashboard

Potential sections:

- Assigned subjects
- Assigned sections
- Take attendance
- Attendance history
- Correction requests
- Attendance reports

## Student Dashboard

Potential sections:

- Overall attendance
- Subject-wise attendance
- Attendance history
- Correction requests
- Request status

---

# 14. Project Folder Structure

The backend should follow a maintainable structure similar to:

```text
smart-attendance/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── students.py
│   │   │   ├── faculty.py
│   │   │   ├── attendance.py
│   │   │   ├── corrections.py
│   │   │   └── reports.py
│   │   │
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── core/
│   │   └── db/
│   │
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── pages/
│   ├── css/
│   └── js/
│
├── docs/
│
├── AGENTS.md
├── REQUIREMENTS.md
├── ARCHITECTURE.md
└── README.md

```

The exact structure may evolve as implementation progresses.

---

# 15. Data Integrity Rules

The database must enforce appropriate integrity rules.

Examples:

- Unique student identifiers
- Unique faculty identifiers
- Unique subject codes
- Foreign key relationships
- Required fields
- Valid attendance statuses
- Prevention of duplicate attendance for the same student, subject, section, and date where appropriate
- Valid user roles

Application-level validation should complement database constraints.

---

# 16. Scalability Considerations

The initial system targets approximately 5,000 students and 200 faculty members.

The architecture should therefore:

- Use a relational database
- Avoid loading unnecessary records
- Use pagination for large lists
- Use indexed columns for frequent queries
- Avoid N+1 database queries
- Separate API, business logic, and database access
- Keep reporting queries efficient
- Allow future frontend replacement without rewriting the backend

The system should be designed so the frontend can later be replaced with React or another frontend framework without replacing the FastAPI backend.

---

# 17. Reporting Architecture

Reports may include:

- Student attendance report
- Subject attendance report
- Section attendance report
- Faculty attendance activity
- Low-attendance report
- Attendance history
- Correction request report

Reports should be generated from database queries rather than storing unnecessary duplicate calculated data.

---

# 18. Auditability

Important attendance-related operations should be auditable.

Examples:

```text
Who performed the action?
What action was performed?
Which record was affected?
When did it happen?
What was changed?

```

This is particularly important for attendance corrections.

---

# 19. Error Handling

The backend should return meaningful HTTP responses.

Examples:

```text
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Validation Error
500 Internal Server Error

```

Errors should not expose sensitive implementation details.

---

# 20. Development Principles

The following principles apply throughout implementation:

1. Do not implement features that are not defined in the requirements unless explicitly approved.
2. Do not change the database design without documenting the change.
3. Keep business logic out of API route handlers where practical.
4. Validate data at the API boundary.
5. Enforce authorization on the backend.
6. Never store plain-text passwords.
7. Use database constraints for critical integrity rules.
8. Keep modules focused on one responsibility.
9. Avoid unnecessary dependencies.
10. Write tests for important business logic.
11. Document significant architectural decisions.
12. Prefer simple, understandable solutions over unnecessary complexity.
13. Do not introduce React or Node.js unless the project requirements later justify them.
14. Keep the backend independent from the frontend implementation.

---

# 21. AI Development Rules

Cursor and Antigravity are development assistants, not architecture decision-makers.

Before making major architectural changes they must:

1. Read `AGENTS.md`.
2. Read `REQUIREMENTS.md`.
3. Read `ARCHITECTURE.md`.
4. Check whether the requested change conflicts with existing requirements.
5. Explain significant architectural changes before implementing them.
6. Avoid silently replacing technologies.
7. Avoid adding unnecessary dependencies.
8. Avoid changing database relationships without documenting the reason.
9. Keep implementation consistent with the agreed architecture.
10. Never remove existing functionality without explicit approval.

---

# 22. Current Architecture Decision

The initial implementation is locked to:

```text
Frontend
HTML + CSS + Minimal JavaScript

Backend
Python + FastAPI

ORM
SQLAlchemy

Database
Microsoft SQL Server

Authentication
JWT + Password Hashing

Testing
Pytest + API Testing

Version Control
Git + GitHub

```

React, Node.js, and PostgreSQL are not part of the initial implementation.

They may only be introduced later if there is a documented requirement or architectural reason.

---

# 23. Implementation Sequence

Implementation must not begin until the architecture and requirements have been reviewed.

The planned sequence is:

```text
1. Requirements
       ↓
2. Architecture
       ↓
3. Database Schema
       ↓
4. Project Setup
       ↓
5. Authentication
       ↓
6. User / Role Management
       ↓
7. Academic Structure
       ↓
8. Attendance Recording
       ↓
9. Attendance History
       ↓
10. Correction Workflow
       ↓
11. Low Attendance Detection
       ↓
12. Reports
       ↓
13. Dashboards
       ↓
14. Testing
       ↓
15. Security Review
       ↓
16. Deployment

```

Each phase should be implemented and tested before moving to the next major phase.

---

# 24. Architecture Status

Status:

**Architecture Draft — Ready for Review**

No implementation should begin until the project owner confirms that this architecture is approved.