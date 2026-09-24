/**
 * Smart Attendance Management System - Centralized Mock Data & Service
 * Provides comprehensive mock datasets when FastAPI endpoints are offline.
 */

const MockDataService = {
  // Departments
  departments: [
    { id: 1, code: 'CSE', name: 'Computer Science & Engineering', is_active: true, total_students: 1450, total_faculty: 45 },
    { id: 2, code: 'ECE', name: 'Electronics & Communication', is_active: true, total_students: 1200, total_faculty: 38 },
    { id: 3, code: 'IT', name: 'Information Technology', is_active: true, total_students: 1100, total_faculty: 35 },
    { id: 4, code: 'ME', name: 'Mechanical Engineering', is_active: true, total_students: 1250, total_faculty: 40 }
  ],

  // Programs
  programs: [
    { id: 1, department_id: 1, code: 'BTECH-CSE', name: 'B.Tech Computer Science', duration: 4 },
    { id: 2, department_id: 2, code: 'BTECH-ECE', name: 'B.Tech Electronics & Communication', duration: 4 },
    { id: 3, department_id: 3, code: 'BTECH-IT', name: 'B.Tech Information Technology', duration: 4 },
    { id: 4, department_id: 4, code: 'BTECH-ME', name: 'B.Tech Mechanical Engineering', duration: 4 }
  ],

  // Sections
  sections: [
    { id: 1, program_id: 1, name: 'Section A', semester: 5, academic_year: '2026', department: 'CSE' },
    { id: 2, program_id: 1, name: 'Section B', semester: 5, academic_year: '2026', department: 'CSE' },
    { id: 3, program_id: 2, name: 'Section A', semester: 3, academic_year: '2026', department: 'ECE' },
    { id: 4, program_id: 3, name: 'Section A', semester: 5, academic_year: '2026', department: 'IT' }
  ],

  // Subjects
  subjects: [
    { id: 1, subject_code: 'CS501', name: 'Data Structures & Algorithms', credits: 4, department_id: 1, department_code: 'CSE', is_active: true },
    { id: 2, subject_code: 'CS502', name: 'Database Management Systems', credits: 4, department_id: 1, department_code: 'CSE', is_active: true },
    { id: 3, subject_code: 'CS503', name: 'Web Technologies & Frameworks', credits: 3, department_id: 1, department_code: 'CSE', is_active: true },
    { id: 4, subject_code: 'EC301', name: 'Digital Electronics & Logic Design', credits: 4, department_id: 2, department_code: 'ECE', is_active: true },
    { id: 5, subject_code: 'IT501', name: 'Software Engineering & Agile', credits: 3, department_id: 3, department_code: 'IT', is_active: true }
  ],

  // Faculty Members
  faculty: [
    { id: 1, employee_identifier: 'FAC-1001', first_name: 'Dr. Rajesh', last_name: 'Sharma', email: 'rajesh.sharma@college.edu', department_id: 1, department_code: 'CSE', assigned_subjects: [1, 2], assigned_sections: [1, 2], is_active: true },
    { id: 2, employee_identifier: 'FAC-1002', first_name: 'Prof. Ananya', last_name: 'Verma', email: 'ananya.verma@college.edu', department_id: 1, department_code: 'CSE', assigned_subjects: [3], assigned_sections: [1], is_active: true },
    { id: 3, employee_identifier: 'FAC-1003', first_name: 'Dr. Vikram', last_name: 'Rao', email: 'vikram.rao@college.edu', department_id: 2, department_code: 'ECE', assigned_subjects: [4], assigned_sections: [3], is_active: true },
    { id: 4, employee_identifier: 'FAC-1004', first_name: 'Prof. Sunita', last_name: 'Kulkarni', email: 'sunita.kulkarni@college.edu', department_id: 3, department_code: 'IT', assigned_subjects: [5], assigned_sections: [4], is_active: true }
  ],

  // Students (Realistic sample with low attendance candidates)
  students: [
    { id: 101, student_identifier: 'STU-2024-001', roll_number: '24CSE001', first_name: 'Aarav', last_name: 'Mehta', email: 'aarav.m@student.college.edu', department_id: 1, department_code: 'CSE', program_id: 1, section_id: 1, section_name: 'Section A', admission_year: 2024, overall_attendance: 92.5, is_active: true },
    { id: 102, student_identifier: 'STU-2024-002', roll_number: '24CSE002', first_name: 'Ananya', last_name: 'Gupta', email: 'ananya.g@student.college.edu', department_id: 1, department_code: 'CSE', program_id: 1, section_id: 1, section_name: 'Section A', admission_year: 2024, overall_attendance: 88.0, is_active: true },
    { id: 103, student_identifier: 'STU-2024-003', roll_number: '24CSE003', first_name: 'Rohan', last_name: 'Singh', email: 'rohan.s@student.college.edu', department_id: 1, department_code: 'CSE', program_id: 1, section_id: 1, section_name: 'Section A', admission_year: 2024, overall_attendance: 64.0, is_active: true }, // Low attendance
    { id: 104, student_identifier: 'STU-2024-004', roll_number: '24CSE004', first_name: 'Diya', last_name: 'Patel', email: 'diya.p@student.college.edu', department_id: 1, department_code: 'CSE', program_id: 1, section_id: 1, section_name: 'Section A', admission_year: 2024, overall_attendance: 95.0, is_active: true },
    { id: 105, student_identifier: 'STU-2024-005', roll_number: '24CSE005', first_name: 'Kabir', last_name: 'Joshi', email: 'kabir.j@student.college.edu', department_id: 1, department_code: 'CSE', program_id: 1, section_id: 1, section_name: 'Section A', admission_year: 2024, overall_attendance: 71.5, is_active: true }, // Low attendance
    { id: 106, student_identifier: 'STU-2024-006', roll_number: '24CSE006', first_name: 'Priya', last_name: 'Deshmukh', email: 'priya.d@student.college.edu', department_id: 1, department_code: 'CSE', program_id: 1, section_id: 2, section_name: 'Section B', admission_year: 2024, overall_attendance: 91.0, is_active: true },
    { id: 107, student_identifier: 'STU-2024-007', roll_number: '24CSE007', first_name: 'Aditya', last_name: 'Nair', email: 'aditya.n@student.college.edu', department_id: 1, department_code: 'CSE', program_id: 1, section_id: 2, section_name: 'Section B', admission_year: 2024, overall_attendance: 68.0, is_active: true }, // Low attendance
    { id: 108, student_identifier: 'STU-2024-008', roll_number: '24ECE001', first_name: 'Siddharth', last_name: 'Reddy', email: 'sid.r@student.college.edu', department_id: 2, department_code: 'ECE', program_id: 2, section_id: 3, section_name: 'Section A', admission_year: 2024, overall_attendance: 84.0, is_active: true }
  ],

  // Attendance Records
  attendanceRecords: [
    { id: 5001, student_id: 101, student_name: 'Aarav Mehta', roll_number: '24CSE001', subject_id: 1, subject_code: 'CS501', subject_name: 'Data Structures & Algorithms', section_id: 1, section_name: 'Section A', faculty_id: 1, faculty_name: 'Dr. Rajesh Sharma', attendance_date: '2026-09-24', session_name: 'Lecture 1', status: 'PRESENT', marked_at: '2026-09-24 09:15:00' },
    { id: 5002, student_id: 102, student_name: 'Ananya Gupta', roll_number: '24CSE002', subject_id: 1, subject_code: 'CS501', subject_name: 'Data Structures & Algorithms', section_id: 1, section_name: 'Section A', faculty_id: 1, faculty_name: 'Dr. Rajesh Sharma', attendance_date: '2026-09-24', session_name: 'Lecture 1', status: 'PRESENT', marked_at: '2026-09-24 09:15:00' },
    { id: 5003, student_id: 103, student_name: 'Rohan Singh', roll_number: '24CSE003', subject_id: 1, subject_code: 'CS501', subject_name: 'Data Structures & Algorithms', section_id: 1, section_name: 'Section A', faculty_id: 1, faculty_name: 'Dr. Rajesh Sharma', attendance_date: '2026-09-24', session_name: 'Lecture 1', status: 'ABSENT', marked_at: '2026-09-24 09:15:00' },
    { id: 5004, student_id: 104, student_name: 'Diya Patel', roll_number: '24CSE004', subject_id: 1, subject_code: 'CS501', subject_name: 'Data Structures & Algorithms', section_id: 1, section_name: 'Section A', faculty_id: 1, faculty_name: 'Dr. Rajesh Sharma', attendance_date: '2026-09-24', session_name: 'Lecture 1', status: 'PRESENT', marked_at: '2026-09-24 09:15:00' },
    { id: 5005, student_id: 105, student_name: 'Kabir Joshi', roll_number: '24CSE005', subject_id: 1, subject_code: 'CS501', subject_name: 'Data Structures & Algorithms', section_id: 1, section_name: 'Section A', faculty_id: 1, faculty_name: 'Dr. Rajesh Sharma', attendance_date: '2026-09-24', session_name: 'Lecture 1', status: 'ABSENT', marked_at: '2026-09-24 09:15:00' },
    { id: 5006, student_id: 101, student_name: 'Aarav Mehta', roll_number: '24CSE001', subject_id: 2, subject_code: 'CS502', subject_name: 'Database Management Systems', section_id: 1, section_name: 'Section A', faculty_id: 1, faculty_name: 'Dr. Rajesh Sharma', attendance_date: '2026-09-23', session_name: 'Lecture 2', status: 'PRESENT', marked_at: '2026-09-23 11:30:00' },
    { id: 5007, student_id: 103, student_name: 'Rohan Singh', roll_number: '24CSE003', subject_id: 2, subject_code: 'CS502', subject_name: 'Database Management Systems', section_id: 1, section_name: 'Section A', faculty_id: 1, faculty_name: 'Dr. Rajesh Sharma', attendance_date: '2026-09-23', session_name: 'Lecture 2', status: 'ABSENT', marked_at: '2026-09-23 11:30:00' }
  ],

  // Correction Requests
  correctionRequests: [
    { id: 301, attendance_id: 5003, student_id: 103, student_name: 'Rohan Singh', roll_number: '24CSE003', subject_code: 'CS501', subject_name: 'Data Structures & Algorithms', date: '2026-09-24', current_status: 'ABSENT', requested_status: 'PRESENT', reason: 'Was present in class, attendance scanner glitch occurred during entry.', status: 'PENDING', requested_at: '2026-09-24 10:30:00', reviewed_by: null, review_comment: null },
    { id: 302, attendance_id: 5007, student_id: 103, student_name: 'Rohan Singh', roll_number: '24CSE003', subject_code: 'CS502', subject_name: 'Database Management Systems', date: '2026-09-23', current_status: 'ABSENT', requested_status: 'PRESENT', reason: 'Medical leave certificate submitted to department office.', status: 'APPROVED', requested_at: '2026-09-23 14:00:00', reviewed_by: 'Dr. Rajesh Sharma', review_comment: 'Medical document verified with admin office.', reviewed_at: '2026-09-23 16:30:00' },
    { id: 303, attendance_id: 5005, student_id: 105, student_name: 'Kabir Joshi', roll_number: '24CSE005', subject_code: 'CS501', subject_name: 'Data Structures & Algorithms', date: '2026-09-24', current_status: 'ABSENT', requested_status: 'PRESENT', reason: 'Arrived 10 minutes late due to traffic.', status: 'REJECTED', requested_at: '2026-09-24 11:00:00', reviewed_by: 'Dr. Rajesh Sharma', review_comment: 'Late arrivals beyond 5 mins marked absent per college policy.', reviewed_at: '2026-09-24 12:00:00' }
  ],

  // Audit Log Entries
  auditLogs: [
    { id: 9001, action: 'ATTENDANCE_RECORDED', entity_type: 'ATTENDANCE', entity_id: '5001', user_name: 'Dr. Rajesh Sharma', role: 'FACULTY', description: 'Marked attendance for CS501 Section A (Present: 4, Absent: 2)', created_at: '2026-09-24 09:15:00' },
    { id: 9002, action: 'CORRECTION_REQUESTED', entity_type: 'CORRECTION', entity_id: '301', user_name: 'Rohan Singh', role: 'STUDENT', description: 'Submitted correction request for CS501 on 2026-09-24', created_at: '2026-09-24 10:30:00' },
    { id: 9003, action: 'CORRECTION_APPROVED', entity_type: 'CORRECTION', entity_id: '302', user_name: 'Dr. Rajesh Sharma', role: 'FACULTY', description: 'Approved correction request for Rohan Singh (CS502)', created_at: '2026-09-23 16:30:00' },
    { id: 9004, action: 'USER_CREATED', entity_type: 'USER', entity_id: '108', user_name: 'System Admin', role: 'ADMIN', description: 'Created new student profile for Siddharth Reddy', created_at: '2026-09-20 14:10:00' }
  ]
};

// Expose MockDataService globally
window.MockDataService = MockDataService;
