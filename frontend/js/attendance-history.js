/**
 * Smart Attendance Management System - Attendance History Controller
 */

const AttendanceHistoryModule = {
  async init() {
    AuthService.protectPage(['ADMIN', 'FACULTY', 'STUDENT']);
    LayoutComponent.init('attendance-history');

    await this.loadFilterDropdowns();
    await this.renderHistoryTable();
    this.setupEventListeners();
  },

  async loadFilterDropdowns() {
    const subjects = await ApiService.getSubjects();
    const sections = await ApiService.getSections();

    const subSelect = document.getElementById('historyFilterSubject');
    const secSelect = document.getElementById('historyFilterSection');

    if (subSelect) {
      subSelect.innerHTML = '<option value="">All Subjects</option>' +
        subjects.map(s => `<option value="${s.id}">${s.subject_code} - ${s.name}</option>`).join('');
    }
    if (secSelect) {
      secSelect.innerHTML = '<option value="">All Sections</option>' +
        sections.map(sec => `<option value="${sec.id}">${sec.name || 'Section A'}</option>`).join('');
    }
  },

  async renderHistoryTable() {
    const user = AuthService.getCurrentUser();
    const subjectId = document.getElementById('historyFilterSubject')?.value || '';
    const sectionId = document.getElementById('historyFilterSection')?.value || '';
    const status = document.getElementById('historyFilterStatus')?.value || '';
    const search = document.getElementById('historyFilterSearch')?.value || '';
    const startDate = document.getElementById('historyStartDate')?.value || '';
    const endDate = document.getElementById('historyEndDate')?.value || '';

    const filters = {};
    if (user.role === 'STUDENT') {
      filters.student_id = user.id;
    }
    if (subjectId) filters.subject_id = subjectId;
    if (sectionId) filters.section_id = sectionId;
    if (status) filters.status = status;

    let records = await ApiService.getAttendanceRecords(filters);

    // Apply date range & search filtering in memory
    if (startDate) {
      records = records.filter(r => r.attendance_date >= startDate);
    }
    if (endDate) {
      records = records.filter(r => r.attendance_date <= endDate);
    }
    if (search) {
      const q = search.toLowerCase();
      records = records.filter(r => 
        (r.student_name && r.student_name.toLowerCase().includes(q)) ||
        (r.roll_number && r.roll_number.toLowerCase().includes(q)) ||
        (r.subject_code && r.subject_code.toLowerCase().includes(q))
      );
    }

    const tableBody = document.getElementById('historyTableBody');
    if (!tableBody) return;

    if (!records || !records.length) {
      tableBody.innerHTML = '<tr><td colspan="8" class="text-muted text-center" style="padding:2.5rem;">No historical attendance records found for the selected filters.</td></tr>';
      document.getElementById('totalHistoryCount').textContent = '0';
      return;
    }

    tableBody.innerHTML = records.map(r => `
      <tr>
        <td><span class="font-bold">${r.attendance_date}</span></td>
        <td><span class="badge badge-neutral">${r.session_name || 'Lecture 1'}</span></td>
        <td>${r.section_name}</td>
        <td><span class="font-semibold">${r.subject_code}</span></td>
        <td>
          <div class="font-semibold">${r.student_name}</div>
          <div class="text-muted" style="font-size:0.75rem;">Roll: ${r.roll_number}</div>
        </td>
        <td>${AppUtils.renderStatusBadge(r.status)}</td>
        <td><span class="text-secondary" style="font-size:0.85rem;">${r.faculty_name}</span></td>
        <td><span class="text-muted" style="font-size:0.75rem;">${r.marked_at}</span></td>
      </tr>
    `).join('');

    document.getElementById('totalHistoryCount').textContent = records.length.toString();
  },

  setupEventListeners() {
    const inputs = [
      'historyFilterSubject',
      'historyFilterSection',
      'historyFilterStatus',
      'historyFilterSearch',
      'historyStartDate',
      'historyEndDate'
    ];

    inputs.forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener('change', () => this.renderHistoryTable());
        if (el.tagName === 'INPUT') el.addEventListener('input', () => this.renderHistoryTable());
      }
    });

    const exportBtn = document.getElementById('exportHistoryCsvBtn');
    if (exportBtn) {
      exportBtn.addEventListener('click', () => this.exportCsv());
    }
  },

  async exportCsv() {
    const user = AuthService.getCurrentUser();
    const records = await ApiService.getAttendanceRecords({ student_id: user.role === 'STUDENT' ? user.id : undefined });
    if (!records || !records.length) {
      AppUtils.showToast('No records available to export.', 'warning');
      return;
    }

    const exportRows = records.map(r => ({
      Date: r.attendance_date,
      Session: r.session_name,
      SubjectCode: r.subject_code,
      SubjectName: r.subject_name,
      Section: r.section_name,
      RollNumber: r.roll_number,
      StudentName: r.student_name,
      Status: r.status,
      Faculty: r.faculty_name,
      MarkedAt: r.marked_at
    }));

    AppUtils.exportToCSV(`Attendance_History_${new Date().toISOString().split('T')[0]}.csv`, exportRows);
    AppUtils.showToast('Attendance history exported to CSV!', 'success');
  }
};

window.AttendanceHistoryModule = AttendanceHistoryModule;
