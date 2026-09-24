# Smart Attendance Management System

A role-based web application designed to help colleges efficiently manage student attendance, attendance corrections, attendance history, low-attendance identification, reporting, and audit tracking.

The system is designed for a college environment with approximately 5,000 students, 200 faculty members, multiple departments, programs, sections, subjects, and academic terms.

---

## 📌 Project Overview

Managing attendance manually in a large college can become difficult because faculty members need to record attendance, students need access to their attendance history, corrections need proper approval, and administrators need institution-wide reports.

The Smart Attendance Management System provides a centralized platform where:

- Administrators manage academic data.
- Faculty members conduct attendance sessions and mark student attendance.
- Students view their attendance and submit correction requests.
- Faculty members review attendance correction requests.
- Administrators and authorized faculty can generate attendance reports.
- The system maintains audit logs for important attendance-related actions.
- Low-attendance students can be identified using configurable thresholds.

---

## 🎯 Objectives

The main objectives of the system are:

1. Digitize the attendance recording process.
2. Reduce manual attendance management.
3. Provide role-based access control.
4. Maintain attendance history.
5. Provide a structured correction workflow.
6. Identify students with low attendance.
7. Generate student, subject, and section attendance reports.
8. Maintain audit logs for important system actions.
9. Provide a scalable architecture for college-level attendance management.
10. Maintain data integrity through database constraints and validation.

---

# 👥 User Roles

The system supports three primary roles.

## 1. Administrator

Administrators have institution-level access.

### Responsibilities

- Manage departments
- Manage academic terms
- Manage programs
- Manage sections
- Manage students
- Manage faculty
- Manage subjects
- Manage faculty assignments
- Manage student enrollments
- View attendance reports
- View low-attendance students
- View audit logs

---

## 2. Faculty

Faculty members have access to classes and subjects assigned to them.

### Responsibilities

- View assigned classes and subjects
- Create attendance sessions
- Mark student attendance
- View attendance history
- Review student correction requests
- Approve or reject correction requests
- View attendance reports for assigned classes

---

## 3. Student

Students have access to their own attendance information.

### Responsibilities

- View personal attendance
- View attendance history
- View subject-wise attendance
- Submit attendance correction requests
- Track correction request status

Students cannot modify attendance directly.

---

# ⭐ Key Features

## Authentication & Authorization

- JWT-based authentication
- Secure password hashing
- Role-based access control
- Protected API endpoints
- Active/inactive user validation
- Unauthorized access protection

---

## Academic Management

The system manages:

- Departments
- Programs
- Academic terms
- Sections
- Subjects
- Faculty
- Students
- Student enrollments
- Faculty assignments

---

## Attendance Management

Faculty can:

1. Select an assigned class/subject.
2. Create an attendance session.
3. Select the session date and time.
4. Enter the topic covered.
5. Mark students as:
   - PRESENT
   - ABSENT
6. Submit attendance.
7. View attendance history.

The backend validates attendance records and prevents duplicate attendance entries.

---

## Attendance Correction Workflow

Students cannot directly modify their attendance.

Instead, they can submit a correction request.

### Workflow

```text
Student
   ↓
Select Attendance Record
   ↓
Submit Correction Request
   ↓
Request Status = PENDING
   ↓
Faculty Reviews Request
   ↓
 ┌───────────────┐
 │               │
Approve        Reject
 │               │
 ↓               ↓
Attendance      Attendance
Updated         Unchanged
 │               │
 └───────┬───────┘
         ↓
      Request Closed
---

# 📈 Data Integrity

The system applies validation rules to maintain reliable attendance data.

Examples include:

- Duplicate attendance sessions are prevented.
- Duplicate student attendance records are prevented.
- Students must belong to valid sections.
- Sections must belong to valid programs.
- Faculty assignments must reference valid entities.
- Subject and department relationships are validated.
- Student enrollments are validated.
- Duplicate pending correction requests are prevented.
- Only pending correction requests can be reviewed.
- Approved or rejected requests cannot be reviewed again.
- Attendance percentage is calculated dynamically.

---

# 🚫 Role Restrictions

| Operation | Admin | Faculty | Student |
|---|---:|---:|---:|
| Manage departments | ✅ | ❌ | ❌ |
| Manage academic structure | ✅ | ❌ | ❌ |
| Manage students | ✅ | ❌ | ❌ |
| Manage faculty | ✅ | ❌ | ❌ |
| Manage subjects | ✅ | ❌ | ❌ |
| Create attendance session | ❌ | ✅ | ❌ |
| Mark attendance | ❌ | ✅ | ❌ |
| View attendance | ✅ | ✅ | Own |
| Submit correction | ❌ | ❌ | Own |
| Review correction | ✅ | Assigned | ❌ |
| View institution reports | ✅ | ❌ | ❌ |
| View assigned-class reports | ✅ | ✅ | ❌ |
| View low attendance | ✅ | Assigned scope | ❌ |
| View audit logs | ✅ | Restricted | ❌ |

Backend authorization is enforced through protected API endpoints and business rules.

---

# 🔮 Future Enhancements

Possible future improvements include:

- Email notifications
- Attendance reminders
- QR-code attendance
- Mobile application
- Biometric integration
- Advanced analytics dashboards
- Export reports to Excel/PDF
- Bulk student import
- Bulk attendance upload
- Notification system
- Cloud deployment
- Redis caching
- Background task processing
- Multi-college support

---

# 📌 Current Project Status

The implemented system includes:

- Authentication
- JWT authorization
- Role-based access control
- Academic management
- Student management
- Faculty management
- Subject management
- Student enrollment
- Faculty assignment
- Attendance session management
- Student attendance
- Attendance correction workflow
- Attendance reports
- Low-attendance identification
- Audit logging
- Role-based frontend dashboards
- REST API integration
- Automated backend testing

---

# 💡 Learning Outcomes

This project demonstrates practical experience with:

- Backend API development
- FastAPI
- REST API design
- SQLAlchemy ORM
- Microsoft SQL Server
- Database relationships
- Authentication and authorization
- JWT
- Password hashing
- Role-based access control
- Business logic implementation
- Repository/service architecture
- Database migrations
- Automated testing
- Frontend API integration
- Git and GitHub
- Software architecture
- Data validation
- Audit logging

---

# 👨‍💻 Author

**Anurag Verma**

B.Tech Computer Science Engineering

GitHub: Add your GitHub profile link here.

github.com/iSam-11

## 📄 License

This project is currently intended as an educational and portfolio project.