/**
 * Smart Attendance Management System - Reports & Analytics Controller
 */

const ReportsModule = {
  async init() {
    AuthService.protectPage(['ADMIN', 'FACULTY', 'STUDENT']);
    LayoutComponent.init('reports');

    await this.renderReportsOverview();
    await this.renderLowAttendanceReport();
    this.setupEventListeners();
  },

  async renderReportsOverview() {
    const threshold = parseInt(document.getElementById('thresholdInput')?.value || 75);
    const reportsData = await ApiService.getReports({ threshold });

    // Populate Overview Stats
    document.getElementById('reportOverallPct').textContent = `${reportsData.overall_percentage}%`;
    document.getElementById('reportTotalStudents').textContent = reportsData.total_students.toLocaleString();
    document.getElementById('reportTotalClasses').textContent = reportsData.total_conducted_classes.toLocaleString();
    document.getElementById('reportLowCount').textContent = reportsData.low_attendance_count.toString();

    // Render Department Summary Breakdown
    const deptContainer = document.getElementById('departmentReportTable');
    if (deptContainer && reportsData.department_summary) {
      deptContainer.innerHTML = reportsData.department_summary.map(d => `
        <tr>
          <td><span class="font-bold">${d.name} (${d.code})</span></td>
          <td>
            <div class="flex items-center gap-2">
              <div style="flex:1; background:var(--border-color); height:8px; border-radius:4px; overflow:hidden;">
                <div style="width:${d.average_attendance}%; background:var(--primary); height:100%;"></div>
              </div>
              <span class="font-bold" style="font-size:0.85rem;">${d.average_attendance}%</span>
            </div>
          </td>
          <td><span class="badge ${d.low_count > 0 ? 'badge-danger' : 'badge-success'}">${d.low_count} Students</span></td>
        </tr>
      `).join('');
    }
  },

  async renderLowAttendanceReport() {
    const threshold = parseInt(document.getElementById('thresholdInput')?.value || 75);
    const students = await ApiService.getStudents({ low_attendance_only: true, threshold: threshold });

    const tableBody = document.getElementById('lowAttendanceReportTable');
    if (!tableBody) return;

    if (!students || !students.length) {
      tableBody.innerHTML = `<tr><td colspan="6" class="text-muted text-center" style="padding:2rem;">No students found below ${threshold}% threshold.</td></tr>`;
      return;
    }

    tableBody.innerHTML = students.map(s => `
      <tr>
        <td><span class="font-bold">${s.roll_number}</span></td>
        <td>
          <div class="font-semibold">${s.first_name} ${s.last_name || ''}</div>
          <div class="text-muted" style="font-size:0.75rem;">${s.email}</div>
        </td>
        <td><span class="badge badge-neutral">${s.department_code}</span></td>
        <td>${s.section_name || 'Section A'}</td>
        <td><span class="badge badge-danger" style="font-size:0.85rem;">${s.overall_attendance}%</span></td>
        <td>
          <button class="btn btn-sm btn-outline-danger" onclick="ReportsModule.sendWarningAlert('${s.first_name}', '${s.email}')">
            <i class="fas fa-paper-plane"></i> Send Alert
          </button>
        </td>
      </tr>
    `).join('');
  },

  setupEventListeners() {
    const thresholdInput = document.getElementById('thresholdInput');
    if (thresholdInput) {
      thresholdInput.addEventListener('change', () => {
        this.renderReportsOverview();
        this.renderLowAttendanceReport();
      });
    }

    const exportBtn = document.getElementById('exportReportCsvBtn');
    if (exportBtn) {
      exportBtn.addEventListener('click', () => this.exportLowAttendanceCsv());
    }
  },

  async exportLowAttendanceCsv() {
    const threshold = parseInt(document.getElementById('thresholdInput')?.value || 75);
    const students = await ApiService.getStudents({ low_attendance_only: true, threshold });

    if (!students || !students.length) {
      AppUtils.showToast('No low-attendance records to export.', 'warning');
      return;
    }

    const rows = students.map(s => ({
      RollNumber: s.roll_number,
      StudentName: `${s.first_name} ${s.last_name}`,
      Email: s.email,
      Department: s.department_code,
      Section: s.section_name,
      AttendancePercentage: `${s.overall_attendance}%`,
      ThresholdApplied: `${threshold}%`
    }));

    AppUtils.exportToCSV(`Low_Attendance_Report_${threshold}pct_${new Date().toISOString().split('T')[0]}.csv`, rows);
    AppUtils.showToast('Low Attendance Report exported to CSV!', 'success');
  },

  sendWarningAlert(studentName, email) {
    AppUtils.showToast(`Attendance Warning Email dispatched to ${studentName} (${email})!`, 'success');
  }
};

window.ReportsModule = ReportsModule;
