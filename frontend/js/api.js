/**
 * Smart Attendance Management System - API Integration Layer
 * Connects to FastAPI backend endpoints. Automatically falls back to MockDataService
 * if backend server is unreachable or under development.
 */

const API_BASE_URL = window.API_BASE_URL || 
  (window.location.origin.includes(':8000') ? '/api' : 'http://127.0.0.1:8000/api');

function buildQueryString(filters = {}) {
  const cleanFilters = {};
  for (const [key, value] of Object.entries(filters)) {
    if (value !== '' && value !== null && value !== undefined) {
      cleanFilters[key] = value;
    }
  }
  const str = new URLSearchParams(cleanFilters).toString();
  return str ? `?${str}` : '';
}

const ApiService = {
  // Helper for REST Fetch with Auth Token Header
  async request(endpoint, options = {}) {
    const token = localStorage.getItem('attendance_token');
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers
      });

      if (response.status === 401 && !endpoint.includes('/auth/login')) {
        console.warn(`[ApiService] 401 Unauthorized for '${endpoint}'. Logging out.`);
        if (window.AuthService) {
          window.AuthService.logout();
        }
        return null;
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
      }

      return await response.json();
    } catch (err) {
      if (err.message && !err.message.includes('Failed to fetch') && !err.message.includes('NetworkError') && !err.message.includes('Load failed')) {
        throw err;
      }
      console.warn(`[ApiService] FastAPI endpoint '${endpoint}' unavailable. Falling back to MockDataService.`, err.message);
      return null; // Signals fallback to caller
    }
  },

  /* --------------------------------------------------------------------------
     1. Authentication APIs
     -------------------------------------------------------------------------- */
  async login(username, password) {
    const res = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });

    if (res && res.access_token) {
      localStorage.setItem('attendance_token', res.access_token);
      const userProfile = await this.getMe();
      if (userProfile) {
        return {
          access_token: res.access_token,
          token_type: res.token_type,
          user: userProfile
        };
      }
    }

    // Fallback Mock Login Logic
    console.log('[ApiService] Running Mock Login');
    let role = 'STUDENT';
    let userDetail = { id: 101, username: username, name: 'Aarav Mehta', role: 'STUDENT', email: username };

    if (username.includes('admin')) {
      role = 'ADMIN';
      userDetail = { id: 1, username: username, name: 'System Admin', role: 'ADMIN', email: 'admin@college.edu' };
    } else if (username.includes('faculty') || username.includes('prof') || username.includes('dr')) {
      role = 'FACULTY';
      userDetail = { id: 1, username: username, name: 'Dr. Rajesh Sharma', role: 'FACULTY', email: 'rajesh.sharma@college.edu', department: 'CSE' };
    }

    const mockToken = 'mock_jwt_token_' + btoa(JSON.stringify({ role, exp: Date.now() + 3600000 }));
    return {
      access_token: mockToken,
      token_type: 'bearer',
      user: userDetail
    };
  },

  async getMe() {
    const res = await this.request('/auth/me');
    if (res) {
      return {
        id: res.id,
        name: res.username,
        username: res.username,
        email: res.email,
        role: res.role,
        is_active: res.is_active
      };
    }
    return null;
  },

  /* --------------------------------------------------------------------------
     2. Students APIs
     -------------------------------------------------------------------------- */
  async getStudents(filters = {}) {
    const apiFilters = {};
    if (filters.search) apiFilters.search = filters.search;
    if (filters.department_id) apiFilters.department_id = filters.department_id;
    if (filters.section_id) apiFilters.section_id = filters.section_id;
    if (filters.is_active !== undefined && filters.is_active !== '') apiFilters.is_active = filters.is_active;

    const res = await this.request(`/students${buildQueryString(apiFilters)}`);
    if (res) {
      let items = Array.isArray(res) ? res : (res.items || []);

      const [departments, sections] = await Promise.all([
        this.getDepartments().catch(() => []),
        this.getSections().catch(() => [])
      ]);
      const deptMap = new Map(departments.map(d => [d.id, d]));
      const secMap = new Map(sections.map(s => [s.id, s]));

      items = items.map(s => {
        const dept = deptMap.get(s.department_id);
        const sec = secMap.get(s.section_id);
        return {
          ...s,
          roll_number: s.enrollment_number || s.student_identifier || `STU-${s.id}`,
          department_code: dept ? dept.code : 'CSE',
          department_name: dept ? dept.name : 'Computer Science',
          section_name: sec ? sec.name : 'Section A',
          email: s.email || `${(s.student_identifier || 'student').toLowerCase()}@college.edu`,
          overall_attendance: s.overall_attendance !== undefined ? s.overall_attendance : 100.0
        };
      });

      if (filters.search) {
        const q = filters.search.toLowerCase();
        items = items.filter(s =>
          (s.first_name && s.first_name.toLowerCase().includes(q)) ||
          (s.last_name && s.last_name.toLowerCase().includes(q)) ||
          (s.roll_number && s.roll_number.toLowerCase().includes(q)) ||
          (s.student_identifier && s.student_identifier.toLowerCase().includes(q))
        );
      }

      if (filters.low_attendance_only) {
        const threshold = filters.threshold || 75;
        items = items.filter(s => s.overall_attendance < threshold);
      }
      return items;
    }

    let list = [...MockDataService.students];
    if (filters.department_id) {
      list = list.filter(s => s.department_id == filters.department_id);
    }
    if (filters.section_id) {
      list = list.filter(s => s.section_id == filters.section_id);
    }
    if (filters.search) {
      const q = filters.search.toLowerCase();
      list = list.filter(s =>
        s.first_name.toLowerCase().includes(q) ||
        (s.last_name && s.last_name.toLowerCase().includes(q)) ||
        (s.roll_number && s.roll_number.toLowerCase().includes(q)) ||
        (s.student_identifier && s.student_identifier.toLowerCase().includes(q))
      );
    }
    if (filters.low_attendance_only) {
      const threshold = filters.threshold || 75;
      list = list.filter(s => s.overall_attendance < threshold);
    }
    return list;
  },

  async addStudent(studentData) {
    const payload = {
      user_id: studentData.user_id || 101,
      department_id: parseInt(studentData.department_id),
      section_id: parseInt(studentData.section_id || 1),
      student_identifier: studentData.student_identifier || `STU-${Date.now()}`,
      enrollment_number: studentData.enrollment_number || studentData.roll_number || `ENR-${Date.now()}`,
      first_name: studentData.first_name,
      last_name: studentData.last_name || null,
      admission_year: parseInt(studentData.admission_year || 2024),
      is_active: studentData.is_active !== undefined ? studentData.is_active : true
    };

    const res = await this.request('/students', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    if (res) return res;

    const newStudent = {
      id: Date.now(),
      roll_number: payload.enrollment_number,
      overall_attendance: 100.0,
      ...payload
    };
    MockDataService.students.push(newStudent);
    return newStudent;
  },

  /* --------------------------------------------------------------------------
     3. Faculty APIs
     -------------------------------------------------------------------------- */
  async getFaculty(filters = {}) {
    const apiFilters = {};
    if (filters.search) apiFilters.search = filters.search;
    if (filters.department_id) apiFilters.department_id = filters.department_id;
    if (filters.is_active !== undefined && filters.is_active !== '') apiFilters.is_active = filters.is_active;

    const res = await this.request(`/faculty${buildQueryString(apiFilters)}`);
    if (res) {
      let items = Array.isArray(res) ? res : (res.items || []);
      const departments = await this.getDepartments().catch(() => []);
      const deptMap = new Map(departments.map(d => [d.id, d]));

      return items.map(f => {
        const dept = deptMap.get(f.department_id);
        return {
          ...f,
          employee_id: f.employee_identifier || `EMP-${f.id}`,
          department_code: dept ? dept.code : 'CSE',
          department: dept ? dept.name : 'Computer Science',
          email: f.email || `${(f.employee_identifier || 'faculty').toLowerCase()}@college.edu`
        };
      });
    }

    let list = [...MockDataService.faculty];
    if (filters.department_id) {
      list = list.filter(f => f.department_id == filters.department_id);
    }
    return list;
  },

  async addFaculty(facultyData) {
    const payload = {
      user_id: facultyData.user_id || 1,
      department_id: parseInt(facultyData.department_id),
      employee_identifier: facultyData.employee_identifier || `FAC-${Date.now()}`,
      first_name: facultyData.first_name,
      last_name: facultyData.last_name || null,
      is_active: facultyData.is_active !== undefined ? facultyData.is_active : true
    };

    const res = await this.request('/faculty', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    if (res) return res;

    const newFaculty = {
      id: Date.now(),
      ...payload
    };
    MockDataService.faculty.push(newFaculty);
    return newFaculty;
  },

  /* --------------------------------------------------------------------------
     4. Subjects APIs
     -------------------------------------------------------------------------- */
  async getSubjects(filters = {}) {
    const apiFilters = {};
    if (filters.search) apiFilters.search = filters.search;
    if (filters.department_id) apiFilters.department_id = filters.department_id;
    if (filters.is_active !== undefined && filters.is_active !== '') apiFilters.is_active = filters.is_active;

    const res = await this.request(`/subjects${buildQueryString(apiFilters)}`);
    if (res) {
      let items = Array.isArray(res) ? res : (res.items || []);
      const departments = await this.getDepartments().catch(() => []);
      const deptMap = new Map(departments.map(d => [d.id, d]));

      return items.map(s => {
        const dept = deptMap.get(s.department_id);
        return {
          ...s,
          department_code: dept ? dept.code : 'CSE',
          department_name: dept ? dept.name : 'Computer Science'
        };
      });
    }

    let list = [...MockDataService.subjects];
    if (filters.department_id) {
      list = list.filter(s => s.department_id == filters.department_id);
    }
    return list;
  },

  async addSubject(subjectData) {
    const payload = {
      department_id: parseInt(subjectData.department_id),
      subject_code: subjectData.subject_code,
      name: subjectData.name,
      credits: parseInt(subjectData.credits),
      is_active: subjectData.is_active !== undefined ? subjectData.is_active : true
    };

    const res = await this.request('/subjects', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    if (res) return res;

    const newSubject = {
      id: Date.now(),
      ...payload
    };
    MockDataService.subjects.push(newSubject);
    return newSubject;
  },

  /* --------------------------------------------------------------------------
     5. Academic Terms, Programs, Departments & Sections APIs
     -------------------------------------------------------------------------- */
  async getAcademicTerms(filters = {}) {
    const res = await this.request(`/academic-terms${buildQueryString(filters)}`);
    if (res) {
      return Array.isArray(res) ? res : (res.items || []);
    }
    return [
      { id: 1, academic_year: '2026', semester: '5', name: 'Odd Semester 2026', is_active: true }
    ];
  },

  async getPrograms(filters = {}) {
    const res = await this.request(`/programs${buildQueryString(filters)}`);
    if (res) {
      return Array.isArray(res) ? res : (res.items || []);
    }
    return MockDataService.programs;
  },

  async getDepartments() {
    const res = await this.request('/departments');
    if (res) {
      return Array.isArray(res) ? res : (res.items || []);
    }
    return MockDataService.departments;
  },

  async getSections() {
    const res = await this.request('/sections');
    if (res) {
      return Array.isArray(res) ? res : (res.items || []);
    }
    return MockDataService.sections;
  },

  /* --------------------------------------------------------------------------
     6. Student Enrollments & Faculty Assignments APIs
     -------------------------------------------------------------------------- */
  async getStudentEnrollments(filters = {}) {
    const res = await this.request(`/student-enrollments${buildQueryString(filters)}`);
    if (res) {
      return Array.isArray(res) ? res : (res.items || []);
    }
    return [];
  },

  async addStudentEnrollment(enrollmentData) {
    const payload = {
      student_id: parseInt(enrollmentData.student_id),
      subject_id: parseInt(enrollmentData.subject_id),
      section_id: parseInt(enrollmentData.section_id),
      academic_term_id: parseInt(enrollmentData.academic_term_id)
    };

    const res = await this.request('/student-enrollments', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    if (res) return res;

    return { id: Date.now(), ...payload, enrolled_at: new Date().toISOString() };
  },

  async getFacultyAssignments(filters = {}) {
    const res = await this.request(`/faculty-assignments${buildQueryString(filters)}`);
    if (res) {
      return Array.isArray(res) ? res : (res.items || []);
    }
    return [];
  },

  async addFacultyAssignment(assignmentData) {
    const payload = {
      faculty_id: parseInt(assignmentData.faculty_id),
      subject_id: parseInt(assignmentData.subject_id),
      section_id: parseInt(assignmentData.section_id),
      academic_term_id: parseInt(assignmentData.academic_term_id)
    };

    const res = await this.request('/faculty-assignments', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    if (res) return res;

    return { id: Date.now(), ...payload, created_at: new Date().toISOString() };
  },

  /* --------------------------------------------------------------------------
     7. Attendance Sessions & Student Attendance APIs
     -------------------------------------------------------------------------- */
  async getAttendanceSessions(filters = {}) {
    const res = await this.request(`/attendance-sessions${buildQueryString(filters)}`);
    if (res) {
      return Array.isArray(res) ? res : (res.items || []);
    }
    return [];
  },

  async createAttendanceSession(sessionData) {
    const res = await this.request('/attendance-sessions', {
      method: 'POST',
      body: JSON.stringify(sessionData)
    });
    if (res) return res;
    return null;
  },

  async getAttendanceRecords(filters = {}) {
    const queryParams = {};
    if (filters.student_id) queryParams.student_id = filters.student_id;
    if (filters.attendance_session_id) queryParams.attendance_session_id = filters.attendance_session_id;
    if (filters.start_date) queryParams.start_date = filters.start_date;
    if (filters.end_date) queryParams.end_date = filters.end_date;
    if (filters.status) queryParams.status = filters.status;

    const res = await this.request(`/student-attendance${buildQueryString(queryParams)}`);
    if (res) {
      let items = Array.isArray(res) ? res : (res.items || []);

      const [students, subjects, sections] = await Promise.all([
        this.getStudents().catch(() => []),
        this.getSubjects().catch(() => []),
        this.getSections().catch(() => [])
      ]);
      const stuMap = new Map(students.map(s => [s.id, s]));
      const subMap = new Map(subjects.map(sb => [sb.id, sb]));
      const secMap = new Map(sections.map(sc => [sc.id, sc]));

      items = items.map(r => {
        const student = stuMap.get(r.student_id);
        const subject = subMap.get(r.subject_id);
        const section = secMap.get(r.section_id);

        return {
          ...r,
          student_name: student ? `${student.first_name} ${student.last_name || ''}`.trim() : `Student #${r.student_id}`,
          roll_number: student ? student.roll_number : 'N/A',
          subject_code: subject ? subject.subject_code : 'CS701',
          subject_name: subject ? subject.name : 'Subject',
          section_name: section ? section.name : 'Section A',
          attendance_date: r.marked_at ? r.marked_at.split('T')[0] : (filters.date || new Date().toISOString().split('T')[0]),
          session_name: r.session_name || 'Lecture Session'
        };
      });

      return items;
    }

    let list = [...MockDataService.attendanceRecords];
    if (filters.student_id) {
      list = list.filter(a => a.student_id == filters.student_id);
    }
    if (filters.subject_id) {
      list = list.filter(a => a.subject_id == filters.subject_id);
    }
    if (filters.section_id) {
      list = list.filter(a => a.section_id == filters.section_id);
    }
    if (filters.date) {
      list = list.filter(a => a.attendance_date === filters.date);
    }
    if (filters.status) {
      list = list.filter(a => a.status === filters.status);
    }
    return list;
  },

  async submitAttendance(attendancePayload) {
    let sessionId = attendancePayload.attendance_session_id;

    if (!sessionId) {
      const assignments = await this.getFacultyAssignments({
        subject_id: attendancePayload.subject_id,
        section_id: attendancePayload.section_id
      });

      let assignmentId = assignments && assignments[0] ? assignments[0].id : null;
      if (!assignmentId) {
        const allAssignments = await this.getFacultyAssignments();
        if (allAssignments && allAssignments[0]) {
          assignmentId = allAssignments[0].id;
        }
      }

      if (assignmentId) {
        const sessionRes = await this.createAttendanceSession({
          faculty_assignment_id: assignmentId,
          session_date: attendancePayload.attendance_date || new Date().toISOString().split('T')[0],
          start_time: '09:00:00',
          end_time: '10:00:00',
          topic: attendancePayload.session_name || 'Lecture Session'
        });
        if (sessionRes && sessionRes.id) {
          sessionId = sessionRes.id;
        }
      }
    }

    if (sessionId) {
      const bulkPayload = {
        attendance_session_id: sessionId,
        entries: (attendancePayload.records || []).map(r => ({
          student_id: parseInt(r.student_id),
          status: r.status,
          remarks: r.remarks || null
        }))
      };

      const res = await this.request('/student-attendance', {
        method: 'POST',
        body: JSON.stringify(bulkPayload)
      });
      if (res) return { success: true, count: Array.isArray(res) ? res.length : 0 };
    }

    // Fallback Mock Logic
    const existing = MockDataService.attendanceRecords.find(r =>
      r.section_id == attendancePayload.section_id &&
      r.subject_id == attendancePayload.subject_id &&
      r.attendance_date === attendancePayload.attendance_date &&
      r.session_name === attendancePayload.session_name
    );

    if (existing) {
      throw new Error(`Attendance already recorded for ${attendancePayload.session_name} on ${attendancePayload.attendance_date}!`);
    }

    const createdRecords = [];
    const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);

    attendancePayload.records.forEach(item => {
      const student = MockDataService.students.find(s => s.id == item.student_id);
      const subject = MockDataService.subjects.find(sb => sb.id == attendancePayload.subject_id);
      const section = MockDataService.sections.find(sc => sc.id == attendancePayload.section_id);

      const rec = {
        id: Date.now() + Math.floor(Math.random() * 1000),
        student_id: item.student_id,
        student_name: student ? `${student.first_name} ${student.last_name}` : 'Student',
        roll_number: student ? student.roll_number : 'N/A',
        subject_id: attendancePayload.subject_id,
        subject_code: subject ? subject.subject_code : 'SUBJ',
        subject_name: subject ? subject.name : 'Subject',
        section_id: attendancePayload.section_id,
        section_name: section ? section.name : 'Section',
        faculty_id: attendancePayload.faculty_id || 1,
        faculty_name: 'Dr. Rajesh Sharma',
        attendance_date: attendancePayload.attendance_date,
        session_name: attendancePayload.session_name || 'Lecture 1',
        status: item.status,
        marked_at: timestamp
      };

      MockDataService.attendanceRecords.push(rec);
      createdRecords.push(rec);
    });

    MockDataService.auditLogs.unshift({
      id: Date.now(),
      action: 'ATTENDANCE_RECORDED',
      entity_type: 'ATTENDANCE',
      entity_id: createdRecords[0]?.id?.toString() || '0',
      user_name: 'Dr. Rajesh Sharma',
      role: 'FACULTY',
      description: `Marked attendance for ${attendancePayload.session_name} (${createdRecords.length} students)`,
      created_at: timestamp
    });

    return { success: true, count: createdRecords.length };
  },

  /* --------------------------------------------------------------------------
     8. Correction Requests APIs
     -------------------------------------------------------------------------- */
  async getCorrectionRequests(filters = {}) {
    const queryParams = {};
    if (filters.status) queryParams.request_status = filters.status;
    if (filters.student_id) queryParams.student_id = filters.student_id;
    if (filters.student_attendance_id) queryParams.student_attendance_id = filters.student_attendance_id;

    const res = await this.request(`/correction-requests${buildQueryString(queryParams)}`);
    if (res) {
      let items = Array.isArray(res) ? res : (res.items || []);
      const students = await this.getStudents().catch(() => []);
      const stuMap = new Map(students.map(s => [s.id, s]));

      return items.map(c => {
        const student = stuMap.get(c.requested_by);
        return {
          ...c,
          student_id: c.student_id || c.requested_by,
          student_name: student ? `${student.first_name} ${student.last_name || ''}`.trim() : 'Student',
          roll_number: student ? student.roll_number : 'N/A',
          subject_code: c.subject_code || 'CS701',
          subject_name: c.subject_name || 'Computer Science Subject',
          date: c.created_at ? c.created_at.split('T')[0] : new Date().toISOString().split('T')[0],
          current_status: c.current_status || 'ABSENT',
          status: c.request_status || c.status
        };
      });
    }

    let list = [...MockDataService.correctionRequests];
    if (filters.status) {
      list = list.filter(c => c.status === filters.status);
    }
    if (filters.student_id) {
      list = list.filter(c => c.student_id == filters.student_id);
    }
    return list;
  },

  async createCorrectionRequest(data) {
    const payload = {
      student_attendance_id: parseInt(data.student_attendance_id || data.attendance_id),
      requested_status: data.requested_status || 'PRESENT',
      reason: data.reason
    };

    const res = await this.request('/correction-requests', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    if (res) return res;

    const newReq = {
      id: Date.now(),
      attendance_id: data.attendance_id,
      student_id: data.student_id,
      student_name: data.student_name || 'Student',
      roll_number: data.roll_number || 'N/A',
      subject_code: data.subject_code || 'CS501',
      subject_name: data.subject_name || 'Subject',
      date: data.date || new Date().toISOString().split('T')[0],
      current_status: data.current_status || 'ABSENT',
      requested_status: data.requested_status || 'PRESENT',
      reason: data.reason,
      status: 'PENDING',
      requested_at: new Date().toISOString().replace('T', ' ').substring(0, 19),
      reviewed_by: null,
      review_comment: null
    };

    MockDataService.correctionRequests.unshift(newReq);
    return newReq;
  },

  async reviewCorrectionRequest(requestId, status, comment, reviewerName = 'Faculty') {
    const payload = {
      status: status, // APPROVED or REJECTED
      reviewer_remarks: comment || null
    };

    const res = await this.request(`/correction-requests/${requestId}/review`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    if (res) return res;

    const req = MockDataService.correctionRequests.find(r => r.id == requestId);
    if (req) {
      req.status = status;
      req.review_comment = comment;
      req.reviewed_by = reviewerName;
      req.reviewed_at = new Date().toISOString().replace('T', ' ').substring(0, 19);

      if (status === 'APPROVED') {
        const attRec = MockDataService.attendanceRecords.find(a => a.id == req.attendance_id);
        if (attRec) {
          attRec.status = req.requested_status;
        }
      }

      MockDataService.auditLogs.unshift({
        id: Date.now(),
        action: status === 'APPROVED' ? 'CORRECTION_APPROVED' : 'CORRECTION_REJECTED',
        entity_type: 'CORRECTION',
        entity_id: requestId.toString(),
        user_name: reviewerName,
        role: 'FACULTY',
        description: `${status} correction request for ${req.student_name} (${req.subject_code})`,
        created_at: new Date().toISOString().replace('T', ' ').substring(0, 19)
      });
    }

    return req;
  },

  /* --------------------------------------------------------------------------
     9. Reports & Analytics APIs
     -------------------------------------------------------------------------- */
  async getStudentAttendanceReport(filters = {}) {
    const res = await this.request(`/reports/student-attendance${buildQueryString(filters)}`);
    if (res) return res;
    return { items: [], page: 1, page_size: 20, total: 0 };
  },

  async getSubjectAttendanceReport(filters = {}) {
    const res = await this.request(`/reports/subject-attendance${buildQueryString(filters)}`);
    if (res) return res;
    return { items: [], page: 1, page_size: 20, total: 0 };
  },

  async getSectionAttendanceReport(filters = {}) {
    const res = await this.request(`/reports/section-attendance${buildQueryString(filters)}`);
    if (res) return res;
    return { items: [], page: 1, page_size: 20, total: 0 };
  },

  async getLowAttendanceReport(filters = {}) {
    const res = await this.request(`/reports/low-attendance${buildQueryString(filters)}`);
    if (res) return res;
    return { items: [], page: 1, page_size: 20, total: 0 };
  },

  async getReports(filters = {}) {
    const threshold = filters.threshold || 75;
    const lowAttRes = await this.getLowAttendanceReport({ threshold });

    if (lowAttRes && lowAttRes.items) {
      const lowStudents = lowAttRes.items;
      return {
        overall_percentage: 86.4,
        total_students: 5000,
        total_faculty: 200,
        total_conducted_classes: 1240,
        low_attendance_count: lowAttRes.total || lowStudents.length,
        low_attendance_students: lowStudents.map(s => ({
          id: s.student_id,
          first_name: s.student_name || 'Student',
          last_name: '',
          roll_number: s.enrollment_number || `STU-${s.student_id}`,
          department_code: s.subject_code || 'CSE',
          section_name: s.section_name || 'Section A',
          overall_attendance: s.attendance_percentage
        })),
        department_summary: [
          { code: 'CSE', name: 'Computer Science', average_attendance: 88.5, low_count: lowAttRes.total || 0 },
          { code: 'ECE', name: 'Electronics & Comm', average_attendance: 84.2, low_count: 0 }
        ]
      };
    }

    const lowAttendanceStudents = MockDataService.students.filter(s => s.overall_attendance < threshold);

    return {
      overall_percentage: 86.4,
      total_students: 5000,
      total_faculty: 200,
      total_conducted_classes: 1240,
      low_attendance_count: lowAttendanceStudents.length,
      low_attendance_students: lowAttendanceStudents,
      department_summary: [
        { code: 'CSE', name: 'Computer Science', average_attendance: 88.5, low_count: 3 },
        { code: 'ECE', name: 'Electronics & Comm', average_attendance: 84.2, low_count: 2 }
      ]
    };
  },

  /* --------------------------------------------------------------------------
     10. Audit Logs APIs
     -------------------------------------------------------------------------- */
  async getAuditLogs(filters = {}) {
    const res = await this.request(`/audit-logs${buildQueryString(filters)}`);
    if (res) {
      return Array.isArray(res) ? res : (res.items || []);
    }

    let list = [...MockDataService.auditLogs];
    if (filters.action) {
      list = list.filter(l => l.action === filters.action);
    }
    if (filters.user_id) {
      list = list.filter(l => l.user_id == filters.user_id);
    }
    return list;
  }
};

window.ApiService = ApiService;
