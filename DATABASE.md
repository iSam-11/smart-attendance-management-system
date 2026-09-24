# Smart Attendance Management System — Database Design

## 1. Database Overview

The system uses:

- **Database:** Microsoft SQL Server
- **ORM:** SQLAlchemy
- **Database access:** Backend service/repository layer
- **Primary key strategy:** Integer identity keys
- **Foreign keys:** Used for relational integrity
- **Timestamps:** Stored for important creation/update operations

The database is designed for approximately:

- 5,000 students
- 200 faculty members
- Multiple departments
- Multiple programs
- Multiple sections
- Multiple subjects
- Multiple academic semesters/years

The design prioritizes:

- Data integrity
- Clear relationships
- Avoiding unnecessary duplication
- Attendance traceability
- Correction workflow
- Reporting
- Future scalability

---

# 2. Entity Overview

The database contains these core entities:

```text
users
departments
programs
sections
students
faculty
subjects
faculty_assignments
student_enrollments
attendance_sessions
student_attendance
correction_requests
audit_logs

```

Relationship overview:

```text
                    ┌──────────────┐
                    │    USERS     │
                    └──────┬───────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
        ┌───────────┐             ┌───────────┐
        │ STUDENTS  │             │  FACULTY  │
        └─────┬─────┘             └─────┬─────┘
              │                         │
              │                         │
              ▼                         ▼
        ┌───────────┐             ┌──────────────┐
        │ SECTIONS  │             │ DEPARTMENTS  │
        └─────┬─────┘             └──────────────┘
              │
              ▼
        ┌─────────────┐
        │  SUBJECTS   │
        └──────┬──────┘
               │
               ▼
      ┌────────────────────┐
      │ FACULTY ASSIGNMENT │
      └─────────┬──────────┘
                │
                ▼
      ┌────────────────────┐
      │ ATTENDANCE SESSION │
      └─────────┬──────────┘
                │
                ▼
      ┌────────────────────┐
      │ STUDENT ATTENDANCE │
      └─────────┬──────────┘
                │
                ▼
      ┌────────────────────┐
      │ CORRECTION REQUEST │
      └────────────────────┘

```

---

# 3. Primary Key Convention

Each major table will use an integer primary key.

Example:

```text
id INT IDENTITY(1,1) PRIMARY KEY

```

The application should normally use these internal IDs for relationships.

Human-readable identifiers such as roll numbers, employee IDs, and subject codes will have separate unique constraints.

---

# 4. Users Table

## Table

```text
users

```

## Purpose

Stores authentication and account information for all system users.

## Columns


| Column        | Type         | Constraints      | Purpose               |
| ------------- | ------------ | ---------------- | --------------------- |
| id            | INT          | PK, Identity     | User identifier       |
| username      | VARCHAR(100) | NOT NULL, UNIQUE | Login identifier      |
| email         | VARCHAR(255) | NOT NULL, UNIQUE | User email            |
| password_hash | VARCHAR(255) | NOT NULL         | Hashed password       |
| role          | VARCHAR(30)  | NOT NULL         | ADMIN/FACULTY/STUDENT |
| is_active     | BIT          | NOT NULL         | Account status        |
| created_at    | DATETIME2    | NOT NULL         | Creation timestamp    |
| updated_at    | DATETIME2    | NOT NULL         | Last update           |


## Rules

- Passwords must never be stored in plain text.
- Username must be unique.
- Email must be unique.
- Role must contain only supported application roles.
- Inactive users cannot authenticate.

---

# 5. Departments Table

## Table

```text
departments

```

## Purpose

Stores academic departments.

## Columns


| Column     | Type         | Constraints      |
| ---------- | ------------ | ---------------- |
| id         | INT          | PK, Identity     |
| name       | VARCHAR(150) | NOT NULL         |
| code       | VARCHAR(30)  | NOT NULL, UNIQUE |
| is_active  | BIT          | NOT NULL         |
| created_at | DATETIME2    | NOT NULL         |


Example:

```text
id | code | name
1  | CSE  | Computer Science and Engineering
2  | ECE  | Electronics and Communication Engineering

```

---

# 6. Programs Table

## Table

```text
programs

```

## Purpose

Represents academic programs offered by departments.

## Columns


| Column         | Type         | Constraints                                  |
| -------------- | ------------ | -------------------------------------------- |
| id             | INT          | PK, Identity                                 |
| department_id  | INT          | FK → [departments.id](http://departments.id) |
| name           | VARCHAR(150) | NOT NULL                                     |
| code           | VARCHAR(30)  | NOT NULL                                     |
| duration_years | INT          | NOT NULL                                     |
| is_active      | BIT          | NOT NULL                                     |
| created_at     | DATETIME2    | NOT NULL                                     |


## Relationship

```text
Department 1 ──────── N Programs

```

A department can have multiple programs.

---

# 7. Sections Table

## Table

```text
sections

```

## Purpose

Represents a class/section for a particular academic period.

## Columns


| Column        | Type        | Constraints                            |
| ------------- | ----------- | -------------------------------------- |
| id            | INT         | PK, Identity                           |
| program_id    | INT         | FK → [programs.id](http://programs.id) |
| name          | VARCHAR(50) | NOT NULL                               |
| academic_year | INT         | NOT NULL                               |
| semester      | INT         | NOT NULL                               |
| is_active     | BIT         | NOT NULL                               |
| created_at    | DATETIME2   | NOT NULL                               |


Example:

```text
Program: B.Tech CSE
Academic Year: 2026
Semester: 5
Section: A

```

## Relationship

```text
Program 1 ──────── N Sections

```

---

# 8. Students Table

## Table

```text
students

```

## Purpose

Stores student profile information.

## Columns


| Column             | Type         | Constraints                                  |
| ------------------ | ------------ | -------------------------------------------- |
| id                 | INT          | PK, Identity                                 |
| user_id            | INT          | FK → [users.id](http://users.id), UNIQUE     |
| student_identifier | VARCHAR(50)  | NOT NULL, UNIQUE                             |
| first_name         | VARCHAR(100) | NOT NULL                                     |
| last_name          | VARCHAR(100) | NULL                                         |
| department_id      | INT          | FK → [departments.id](http://departments.id) |
| program_id         | INT          | FK → [programs.id](http://programs.id)       |
| section_id         | INT          | FK → [sections.id](http://sections.id)       |
| admission_year     | INT          | NOT NULL                                     |
| is_active          | BIT          | NOT NULL                                     |
| created_at         | DATETIME2    | NOT NULL                                     |
| updated_at         | DATETIME2    | NOT NULL                                     |


## Relationship

```text
User 1 ─────── 0..1 Student

Department 1 ─────── N Students

Program 1 ─────── N Students

Section 1 ─────── N Students

```

The `student_identifier` should represent the institution's student/roll number.

---

# 9. Faculty Table

## Table

```text
faculty

```

## Purpose

Stores faculty profile information.

## Columns


| Column              | Type         | Constraints                                  |
| ------------------- | ------------ | -------------------------------------------- |
| id                  | INT          | PK, Identity                                 |
| user_id             | INT          | FK → [users.id](http://users.id), UNIQUE     |
| employee_identifier | VARCHAR(50)  | NOT NULL, UNIQUE                             |
| first_name          | VARCHAR(100) | NOT NULL                                     |
| last_name           | VARCHAR(100) | NULL                                         |
| department_id       | INT          | FK → [departments.id](http://departments.id) |
| is_active           | BIT          | NOT NULL                                     |
| created_at          | DATETIME2    | NOT NULL                                     |
| updated_at          | DATETIME2    | NOT NULL                                     |


## Relationship

```text
User 1 ─────── 0..1 Faculty

Department 1 ─────── N Faculty

```

---

# 10. Subjects Table

## Table

```text
subjects

```

## Purpose

Stores academic subjects.

## Columns


| Column        | Type         | Constraints                                  |
| ------------- | ------------ | -------------------------------------------- |
| id            | INT          | PK, Identity                                 |
| department_id | INT          | FK → [departments.id](http://departments.id) |
| subject_code  | VARCHAR(30)  | NOT NULL, UNIQUE                             |
| name          | VARCHAR(150) | NOT NULL                                     |
| credits       | DECIMAL(3,1) | NULL                                         |
| is_active     | BIT          | NOT NULL                                     |
| created_at    | DATETIME2    | NOT NULL                                     |


## Relationship

```text
Department 1 ─────── N Subjects

```

---

# 11. Faculty Assignments Table

## Table

```text
faculty_assignments

```

## Purpose

Defines which faculty member teaches which subject to which section.

This table is important for authorization.

A faculty member should not automatically have permission to modify attendance for every subject.

## Columns


| Column        | Type      | Constraints                            |
| ------------- | --------- | -------------------------------------- |
| id            | INT       | PK, Identity                           |
| faculty_id    | INT       | FK → [faculty.id](http://faculty.id)   |
| subject_id    | INT       | FK → [subjects.id](http://subjects.id) |
| section_id    | INT       | FK → [sections.id](http://sections.id) |
| academic_year | INT       | NOT NULL                               |
| semester      | INT       | NOT NULL                               |
| is_active     | BIT       | NOT NULL                               |
| created_at    | DATETIME2 | NOT NULL                               |


## Relationship

```text
Faculty
   │
   ├──── Subject
   │
   └──── Section

```

This creates the teaching assignment.

## Important Constraint

The database/application should prevent duplicate active assignments for the same:

```text
faculty + subject + section + academic_year + semester

```

---

# 12. Student Enrollments Table

## Table

```text
student_enrollments

```

## Purpose

Defines which students are enrolled in which subject.

## Columns


| Column        | Type      | Constraints                            |
| ------------- | --------- | -------------------------------------- |
| id            | INT       | PK, Identity                           |
| student_id    | INT       | FK → [students.id](http://students.id) |
| subject_id    | INT       | FK → [subjects.id](http://subjects.id) |
| section_id    | INT       | FK → [sections.id](http://sections.id) |
| academic_year | INT       | NOT NULL                               |
| semester      | INT       | NOT NULL                               |
| enrolled_at   | DATETIME2 | NOT NULL                               |
| is_active     | BIT       | NOT NULL                               |


## Important Constraint

A student should not have duplicate active enrollment for the same:

```text
student + subject + section + academic_year + semester

```

---

# 13. Attendance Sessions Table

## Table

```text
attendance_sessions

```

## Purpose

Represents one actual class/lecture during which attendance is taken.

This is the parent entity for individual student attendance records.

## Columns


| Column                | Type        | Constraints                                          |
| --------------------- | ----------- | ---------------------------------------------------- |
| id                    | INT         | PK, Identity                                         |
| faculty_assignment_id | INT         | FK → faculty_[assignments.id](http://assignments.id) |
| attendance_date       | DATE        | NOT NULL                                             |
| period_number         | INT         | NULL                                                 |
| start_time            | TIME        | NULL                                                 |
| end_time              | TIME        | NULL                                                 |
| classroom             | VARCHAR(50) | NULL                                                 |
| created_at            | DATETIME2   | NOT NULL                                             |
| updated_at            | DATETIME2   | NOT NULL                                             |


## Example

```text
Session ID: 1052
Faculty: Faculty 12
Subject: DBMS
Section: CSE-A
Date: 2026-09-24
Period: 3
Classroom: Room 204

```

## Important Constraint

The system should prevent duplicate sessions for the same assignment, date, and period where the academic rules require uniqueness.

---

# 14. Student Attendance Table

## Table

```text
student_attendance

```

## Purpose

Stores the attendance status of an individual student for an attendance session.

## Columns


| Column                | Type        | Constraints                                       |
| --------------------- | ----------- | ------------------------------------------------- |
| id                    | INT         | PK, Identity                                      |
| attendance_session_id | INT         | FK → attendance_[sessions.id](http://sessions.id) |
| student_id            | INT         | FK → [students.id](http://students.id)            |
| status                | VARCHAR(20) | NOT NULL                                          |
| marked_at             | DATETIME2   | NOT NULL                                          |
| updated_at            | DATETIME2   | NOT NULL                                          |


Possible statuses:

```text
PRESENT
ABSENT

```

Future statuses can be added if the requirements justify them.

## Important Constraint

A student can have only one attendance record per session.

Therefore:

```text
UNIQUE(attendance_session_id, student_id)

```

---

# 15. Correction Requests Table

## Table

```text
correction_requests

```

## Purpose

Stores student requests to correct an attendance record.

## Columns


| Column                | Type          | Constraints                                        |
| --------------------- | ------------- | -------------------------------------------------- |
| id                    | INT           | PK, Identity                                       |
| student_attendance_id | INT           | FK → student_[attendance.id](http://attendance.id) |
| student_id            | INT           | FK → [students.id](http://students.id)             |
| reason                | VARCHAR(1000) | NOT NULL                                           |
| requested_status      | VARCHAR(20)   | NOT NULL                                           |
| status                | VARCHAR(20)   | NOT NULL                                           |
| reviewed_by           | INT           | FK → [faculty.id](http://faculty.id), NULL         |
| review_comment        | VARCHAR(1000) | NULL                                               |
| created_at            | DATETIME2     | NOT NULL                                           |
| reviewed_at           | DATETIME2     | NULL                                               |


Possible request statuses:

```text
PENDING
APPROVED
REJECTED

```

## Workflow

```text
Student
   ↓
Correction Request
   ↓
PENDING
   ↓
Faculty Review
   ├─────────────┐
   ▼             ▼
APPROVED       REJECTED
   │
   ▼
Attendance Updated

```

A student must not directly change their own attendance.

---

# 16. Audit Logs Table

## Table

```text
audit_logs

```

## Purpose

Records important system actions for traceability.

## Columns


| Column      | Type          | Constraints                      |
| ----------- | ------------- | -------------------------------- |
| id          | BIGINT        | PK, Identity                     |
| user_id     | INT           | FK → [users.id](http://users.id) |
| action      | VARCHAR(100)  | NOT NULL                         |
| entity_type | VARCHAR(100)  | NOT NULL                         |
| entity_id   | INT           | NULL                             |
| description | VARCHAR(2000) | NULL                             |
| created_at  | DATETIME2     | NOT NULL                         |


Examples:

```text
ATTENDANCE_CREATED
ATTENDANCE_UPDATED
CORRECTION_REQUESTED
CORRECTION_APPROVED
CORRECTION_REJECTED
USER_CREATED
USER_UPDATED

```

Audit logs should generally be append-only.

---

# 17. Relationship Summary

```text
USERS
 │
 ├────────────── STUDENTS
 │
 └────────────── FACULTY
                       │
                       ▼
                 FACULTY_ASSIGNMENTS
                  │       │       │
                  │       │       └── SECTIONS
                  │       │
                  │       └────────── SUBJECTS
                  │
                  └────────────── FACULTY


DEPARTMENTS
 │
 ├── PROGRAMS
 │      │
 │      └── SECTIONS
 │             │
 │             └── STUDENTS
 │
 ├── FACULTY
 │
 └── SUBJECTS


STUDENTS
 │
 └── STUDENT_ENROLLMENTS
              │
              └── SUBJECTS


FACULTY_ASSIGNMENTS
 │
 └── ATTENDANCE_SESSIONS
              │
              └── STUDENT_ATTENDANCE
                          │
                          └── CORRECTION_REQUESTS


USERS
 │
 └── AUDIT_LOGS

```

---

# 18. Cardinality

The major relationships are:


| Relationship                             | Cardinality |
| ---------------------------------------- | ----------- |
| Department → Programs                    | 1:N         |
| Department → Faculty                     | 1:N         |
| Department → Students                    | 1:N         |
| Department → Subjects                    | 1:N         |
| Program → Sections                       | 1:N         |
| Section → Students                       | 1:N         |
| User → Student                           | 1:0..1      |
| User → Faculty                           | 1:0..1      |
| Faculty → Faculty Assignments            | 1:N         |
| Subject → Faculty Assignments            | 1:N         |
| Section → Faculty Assignments            | 1:N         |
| Student → Enrollments                    | 1:N         |
| Subject → Enrollments                    | 1:N         |
| Faculty Assignment → Attendance Sessions | 1:N         |
| Attendance Session → Student Attendance  | 1:N         |
| Student → Student Attendance             | 1:N         |
| Student Attendance → Correction Requests | 1:N         |
| User → Audit Logs                        | 1:N         |


---

# 19. Important Database Constraints

The database and application must enforce:

## Identity Constraints

- User username unique
- User email unique
- Student identifier unique
- Faculty employee identifier unique
- Department code unique
- Subject code unique

## Relationship Constraints

- Valid foreign keys
- Student must belong to a valid section
- Section must belong to a valid program
- Program must belong to a valid department
- Faculty must belong to a valid department
- Subject must belong to a valid department

## Attendance Constraints

- One student attendance record per session
- Attendance session must belong to a valid faculty assignment
- Attendance cannot be recorded for a student who is not eligible/enrolled
- Duplicate attendance sessions should be prevented according to session uniqueness rules

## Correction Constraints

- Correction must reference an existing attendance record
- Only authorized users can approve/reject requests
- Students cannot approve their own requests
- Approved corrections must be auditable

---

# 20. Recommended Indexes

Indexes should be added for frequently queried columns.

Initial candidates:

```text
users.username
users.email

students.student_identifier
students.section_id
students.department_id

faculty.employee_identifier
faculty.department_id

subjects.subject_code
subjects.department_id

faculty_assignments.faculty_id
faculty_assignments.subject_id
faculty_assignments.section_id

student_enrollments.student_id
student_enrollments.subject_id
student_enrollments.section_id

attendance_sessions.faculty_assignment_id
attendance_sessions.attendance_date

student_attendance.attendance_session_id
student_attendance.student_id

correction_requests.student_id
correction_requests.status
correction_requests.student_attendance_id

audit_logs.user_id
audit_logs.created_at

```

Indexes should be added based on actual query patterns and performance testing rather than indexing every column.

---

# 21. Attendance Percentage Calculation

Attendance percentage should normally be calculated from attendance records rather than permanently storing the percentage.

Formula:

```text
Attendance Percentage =
(Present Attendance / Total Attendance Sessions) × 100

```

Example:

```text
Total Sessions = 30
Present = 24

Attendance =
24 / 30 × 100
= 80%

```

This avoids stale calculated values.

The application can calculate:

- Overall attendance
- Subject-wise attendance
- Section attendance statistics
- Low-attendance lists

---

# 22. Low Attendance Query Concept

The application should identify students whose attendance percentage falls below the configured threshold.

Conceptually:

```text
For each student:
    Calculate total sessions
    Calculate present sessions
    Calculate percentage

    If percentage < configured threshold:
        Include in low-attendance report

```

The threshold should be configurable at the application/business-rule level.

---

# 23. Academic Period Handling

Attendance and enrollment are tied to:

- Academic year
- Semester

This prevents historical data from being mixed with future academic periods.

Example:

```text
Academic Year: 2026
Semester: 5

```

The same student can therefore have different subject enrollments in another semester.

Historical attendance must remain preserved.

---

# 24. Deletion Strategy

Attendance and audit history are important records and should generally not be physically deleted through normal application workflows.

Instead, use:

- `is_active`
- Status changes
- Audit records

where appropriate.

For example, deactivating a student should not delete their historical attendance.

---

# 25. Transaction Requirements

Operations involving multiple database changes should use database transactions.

Example:

```text
Create Attendance Session
        ↓
Create Student Attendance Records
        ↓
Create Audit Log
        ↓
COMMIT

```

If a critical step fails:

```text
ROLLBACK

```

This prevents partially saved attendance sessions.

---

# 26. ORM Mapping

SQLAlchemy models will map to these tables.

Example conceptual mapping:

```text
User                → users
Student             → students
Faculty             → faculty
Department          → departments
Program             → programs
Section             → sections
Subject             → subjects
FacultyAssignment   → faculty_assignments
StudentEnrollment   → student_enrollments
AttendanceSession   → attendance_sessions
StudentAttendance   → student_attendance
CorrectionRequest   → correction_requests
AuditLog            → audit_logs

```

SQLAlchemy relationships should represent the documented foreign-key relationships.

---

# 27. Database Naming Convention

Use:

- `snake_case` for table names
- `snake_case` for column names
- Singular Python model names
- Plural database table names

Example:

```text
Python:
AttendanceSession

Database:
attendance_sessions

```

---

# 28. Database Migration

Database schema changes must be handled through a migration system rather than manually modifying production tables.

The implementation should use an appropriate migration tool compatible with SQLAlchemy.

Schema changes should be:

- Version controlled
- Reviewable
- Reproducible
- Applied consistently across environments

---

# 29. Database Security

The application must:

- Never expose database credentials to the frontend
- Store credentials in environment variables
- Never commit secrets to Git
- Use a dedicated database user for the application
- Apply appropriate database permissions
- Use secure connections where required by the deployment environment

Example environment variables:

```text
DATABASE_URL
DB_SERVER
DB_NAME
DB_USER
DB_PASSWORD
JWT_SECRET_KEY

```

Actual credentials must never be committed to the repository.

---

# 30. Final Database Design Decision

The database architecture is based on:

```text
Microsoft SQL Server
        │
        ▼
SQLAlchemy
        │
        ▼
FastAPI

```

Attendance is represented as:

```text
Faculty Assignment
        ↓
Attendance Session
        ↓
Student Attendance
        ↓
Correction Request

```

This design is the authoritative database structure for the initial implementation.

Any structural change must be documented and reviewed before implementation.

---

# 31. Database Status

Status:

**Database Design — Ready for Review**

No production database tables should be created until this design has been reviewed and approved.

No AI coding agent should generate SQLAlchemy models until this document is approved.