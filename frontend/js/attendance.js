/**
 * Smart Attendance Management System - Attendance Recording Controller
 */

const AttendanceModule = {
  // Local state for current recording session
  currentStudentsState: [],

  async init() {
    AuthService.protectPage(['ADMIN', 'FACULTY']);
    LayoutComponent.init('attendance');

    await this.loadDropdownOptions();

    // Check URL parameters for pre-selected subject/section
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('subject')) {
      const subSelect = document.getElementById('attendanceSubjectSelect');
      if (subSelect) subSelect.value = urlParams.get('subject');
    }
    if (urlParams.has('section')) {
      const secSelect = document.getElementById('attendanceSectionSelect');
      if (secSelect) secSelect.value = urlParams.get('section');
    }

    // Set default date to today
    const dateInput = document.getElementById('attendanceDateInput');
    if (dateInput) {
      dateInput.value = new Date().toISOString().split('T')[0];
    }

    await this.loadEnrolledStudents();
    this.setupEventListeners();
  },

  async loadDropdownOptions() {
    const subjects = await ApiService.getSubjects();
    const sections = await ApiService.getSections();

    const subSelect = document.getElementById('attendanceSubjectSelect');
    const secSelect = document.getElementById('attendanceSectionSelect');

    if (subSelect) {
      subSelect.innerHTML = subjects.map(s => `<option value="${s.id}">${s.subject_code} - ${s.name}</option>`).join('');
    }
    if (secSelect) {
      secSelect.innerHTML = sections.map(sec => `<option value="${sec.id}">${sec.name || 'Section A'}</option>`).join('');
    }
  },

  async loadEnrolledStudents() {
    const sectionId = document.getElementById('attendanceSectionSelect')?.value || 1;
    const students = await ApiService.getStudents({ section_id: sectionId });

    // Initialize local state (Default status: PRESENT)
    this.currentStudentsState = students.map(s => ({
      student_id: s.id,
      roll_number: s.roll_number,
      first_name: s.first_name,
      last_name: s.last_name || '',
      overall_attendance: s.overall_attendance,
      status: 'PRESENT'
    }));

    this.renderStudentsGrid();
    this.updateAttendanceStats();
  },

  renderStudentsGrid() {
    const container = document.getElementById('attendanceStudentsContainer');
    if (!container) return;

    if (!this.currentStudentsState || !this.currentStudentsState.length) {
      container.innerHTML = '<div class="text-muted text-center" style="padding:3rem;">No students enrolled in this section.</div>';
      return;
    }

    container.innerHTML = this.currentStudentsState.map((s, index) => `
      <div class="card" style="padding:1rem;">
        <div class="flex justify-between items-center">
          <div>
            <div class="font-bold">${s.first_name} ${s.last_name}</div>
            <div class="text-muted" style="font-size:0.75rem;">Roll: ${s.roll_number} • Current Att: ${s.overall_attendance}%</div>
          </div>
          <div class="flex items-center gap-2">
            <button class="btn btn-sm ${s.status === 'PRESENT' ? 'btn-success' : 'btn-secondary'}"
                    onclick="AttendanceModule.toggleStatus(${index}, 'PRESENT')">
              <i class="fas fa-check"></i> Present
            </button>
            <button class="btn btn-sm ${s.status === 'ABSENT' ? 'btn-danger' : 'btn-secondary'}"
                    onclick="AttendanceModule.toggleStatus(${index}, 'ABSENT')">
              <i class="fas fa-times"></i> Absent
            </button>
          </div>
        </div>
      </div>
    `).join('');
  },

  toggleStatus(index, newStatus) {
    if (this.currentStudentsState[index]) {
      this.currentStudentsState[index].status = newStatus;
      this.renderStudentsGrid();
      this.updateAttendanceStats();
    }
  },

  markAll(status) {
    this.currentStudentsState.forEach(s => s.status = status);
    this.renderStudentsGrid();
    this.updateAttendanceStats();
  },

  updateAttendanceStats() {
    const total = this.currentStudentsState.length;
    const present = this.currentStudentsState.filter(s => s.status === 'PRESENT').length;
    const absent = total - present;
    const pct = AppUtils.calculateAttendancePercentage(present, total);

    document.getElementById('statTotalEnrolled').textContent = total.toString();
    document.getElementById('statPresentCount').textContent = present.toString();
    document.getElementById('statAbsentCount').textContent = absent.toString();
    document.getElementById('statSessionPercentage').textContent = `${pct}%`;
  },

  setupEventListeners() {
    const secSelect = document.getElementById('attendanceSectionSelect');
    if (secSelect) {
      secSelect.addEventListener('change', () => this.loadEnrolledStudents());
    }

    const submitBtn = document.getElementById('submitAttendanceBtn');
    if (submitBtn) {
      submitBtn.addEventListener('click', () => this.handleSubmitAttendance());
    }
  },

  async handleSubmitAttendance() {
    const subjectId = parseInt(document.getElementById('attendanceSubjectSelect').value);
    const sectionId = parseInt(document.getElementById('attendanceSectionSelect').value);
    const attendanceDate = document.getElementById('attendanceDateInput').value;
    const sessionName = document.getElementById('attendanceSessionSelect').value;

    if (!attendanceDate) {
      AppUtils.showToast('Please select a valid attendance date!', 'warning');
      return;
    }

    const payload = {
      subject_id: subjectId,
      section_id: sectionId,
      attendance_date: attendanceDate,
      session_name: sessionName,
      records: this.currentStudentsState.map(s => ({
        student_id: s.student_id,
        status: s.status
      }))
    };

    try {
      const res = await ApiService.submitAttendance(payload);
      AppUtils.showToast(`Attendance successfully submitted for ${payload.records.length} students!`, 'success');
      
      // Redirect to history page after 1.5s
      setTimeout(() => {
        window.location.href = 'attendance-history.html';
      }, 1500);
    } catch (err) {
      AppUtils.showToast(err.message, 'danger');
    }
  }
};

window.AttendanceModule = AttendanceModule;
