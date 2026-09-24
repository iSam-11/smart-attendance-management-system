/**
 * Smart Attendance Management System - Role-Based Dashboard Controller
 */

const DashboardModule = {
  async initAdminDashboard() {
    AuthService.protectPage(['ADMIN']);
    LayoutComponent.init('dashboard');

    const students = await ApiService.getStudents();
    const faculty = await ApiService.getFaculty();
    const departments = await ApiService.getDepartments();
    const corrections = await ApiService.getCorrectionRequests();
    const reports = await ApiService.getReports();

    // Populate Metrics
    document.getElementById('metric-total-students').textContent = (students ? students.length : 0).toString();
    document.getElementById('metric-total-faculty').textContent = (faculty ? faculty.length : 0).toString();
    document.getElementById('metric-departments').textContent = departments.length.toString();
    document.getElementById('metric-overall-attendance').textContent = `${reports.overall_percentage}%`;
    document.getElementById('metric-pending-corrections').textContent = corrections.filter(c => c.status === 'PENDING').length.toString();

    // Render Low Attendance Table
    this.renderLowAttendanceWidget(reports.low_attendance_students);

    // Render System Audit Log Feed
    this.renderAuditLogFeed();
  },

  async initFacultyDashboard() {
    AuthService.protectPage(['FACULTY']);
    LayoutComponent.init('dashboard');

    const facultyUser = AuthService.getCurrentUser();
    const subjects = await ApiService.getSubjects();
    const sections = await ApiService.getSections();
    const corrections = await ApiService.getCorrectionRequests({ status: 'PENDING' });
    const students = await ApiService.getStudents({ low_attendance_only: true });

    // Populate Metrics
    document.getElementById('metric-assigned-subjects').textContent = subjects.length.toString();
    document.getElementById('metric-assigned-sections').textContent = sections.length.toString();
    document.getElementById('metric-pending-reviews').textContent = corrections.length.toString();
    document.getElementById('metric-low-students').textContent = students.length.toString();

    // Render Assigned Classes List
    this.renderFacultyAssignedClasses(subjects, sections);

    // Render Pending Correction Reviews
    this.renderPendingCorrections(corrections);
  },

  async initStudentDashboard() {
    AuthService.protectPage(['STUDENT']);
    LayoutComponent.init('dashboard');

    const user = AuthService.getCurrentUser();
    const myRecords = await ApiService.getAttendanceRecords({ student_id: user.id });
    const myCorrections = await ApiService.getCorrectionRequests({ student_id: user.id });

    // Calculate personal attendance
    const presentCount = myRecords.filter(r => r.status === 'PRESENT').length;
    const totalConducted = myRecords.length || 1;
    const percentage = AppUtils.calculateAttendancePercentage(presentCount, totalConducted);

    // Set Percentage Metric
    const percentageEl = document.getElementById('student-overall-percentage');
    if (percentageEl) percentageEl.textContent = `${percentage}%`;

    // Low Attendance Alert Banner check (< 75% threshold)
    const alertBanner = document.getElementById('student-low-alert');
    if (alertBanner) {
      if (percentage < 75) {
        alertBanner.style.display = 'flex';
      } else {
        alertBanner.style.display = 'none';
      }
    }

    // Render Subject breakdown
    this.renderStudentSubjectBreakdown(myRecords);

    // Render Correction requests timeline
    this.renderStudentCorrections(myCorrections);
  },

  /* Helper Renderers */
  renderLowAttendanceWidget(lowStudents) {
    const container = document.getElementById('low-attendance-list');
    if (!container) return;

    if (!lowStudents || !lowStudents.length) {
      container.innerHTML = '<tr><td colspan="4" class="text-muted">No students below 75% threshold.</td></tr>';
      return;
    }

    container.innerHTML = lowStudents.map(s => `
      <tr>
        <td>
          <div class="font-semibold">${s.first_name} ${s.last_name}</div>
          <div class="text-muted" style="font-size:0.75rem;">${s.roll_number}</div>
        </td>
        <td>${s.department_code} / ${s.section_name}</td>
        <td><span class="badge badge-danger">${s.overall_attendance}%</span></td>
        <td>
          <a href="students.html?search=${s.roll_number}" class="btn btn-sm btn-secondary">
            <i class="fas fa-eye"></i> Details
          </a>
        </td>
      </tr>
    `).join('');
  },

  async renderAuditLogFeed() {
    const container = document.getElementById('audit-log-feed');
    if (!container) return;

    const logs = await ApiService.getAuditLogs({ page_size: 5 });
    if (!logs || !logs.length) {
      container.innerHTML = '<div class="text-muted" style="padding:1rem;">No recent audit activity.</div>';
      return;
    }

    container.innerHTML = logs.slice(0, 5).map(l => {
      const action = l.action || '';
      const dotClass = action.includes('APPROVED') || action.includes('MARKED') || action.includes('RECORDED')
        ? 'success'
        : (action.includes('REJECTED') ? 'danger' : '');
      const desc = l.description || `${l.action} on ${l.entity_type} #${l.entity_id}`;
      const userName = l.user_name || l.actor_username || `User #${l.user_id || 'System'}`;
      const createdAt = l.created_at ? (typeof l.created_at === 'string' ? l.created_at.replace('T', ' ').substring(0, 19) : l.created_at) : '';

      return `
        <div class="timeline-item">
          <div class="timeline-dot ${dotClass}"></div>
          <div class="timeline-title">${desc}</div>
          <div class="timeline-time"><i class="fas fa-user-circle"></i> ${userName} • ${createdAt}</div>
        </div>
      `;
    }).join('');
  },

  renderFacultyAssignedClasses(subjects, sections) {
    const container = document.getElementById('faculty-classes-grid');
    if (!container) return;

    container.innerHTML = subjects.map((sub, idx) => {
      const sec = sections[idx % sections.length];
      return `
        <div class="card">
          <div class="card-header">
            <span class="badge badge-info">${sub.subject_code}</span>
            <span class="text-muted" style="font-size:0.8rem;">${sec.name}</span>
          </div>
          <div class="card-body">
            <h4>${sub.name}</h4>
            <p class="text-secondary" style="font-size:0.85rem; margin-top:0.3rem;">
              Department: ${sub.department_code || 'CSE'} • Credits: ${sub.credits}
            </p>
          </div>
          <div class="card-footer">
            <a href="attendance.html?subject=${sub.id}&section=${sec.id}" class="btn btn-sm btn-primary w-full">
              <i class="fas fa-clipboard-check"></i> Take Attendance
            </a>
          </div>
        </div>
      `;
    }).join('');
  },

  renderPendingCorrections(corrections) {
    const container = document.getElementById('pending-corrections-list');
    if (!container) return;

    if (!corrections || !corrections.length) {
      container.innerHTML = '<tr><td colspan="5" class="text-muted">No pending correction requests.</td></tr>';
      return;
    }

    container.innerHTML = corrections.map(c => `
      <tr>
        <td>
          <div class="font-semibold">${c.student_name}</div>
          <div class="text-muted" style="font-size:0.75rem;">${c.roll_number}</div>
        </td>
        <td>${c.subject_code} • ${c.date}</td>
        <td><span class="badge badge-neutral">${c.current_status} → ${c.requested_status}</span></td>
        <td><span class="text-secondary" style="font-size:0.85rem;">"${c.reason}"</span></td>
        <td>
          <a href="corrections.html" class="btn btn-sm btn-primary">
            Review
          </a>
        </td>
      </tr>
    `).join('');
  },

  async renderStudentSubjectBreakdown(myRecords) {
    const container = document.getElementById('student-subject-table');
    if (!container) return;

    const subjects = await ApiService.getSubjects();
    
    container.innerHTML = subjects.map(sub => {
      const subRecords = myRecords.filter(r => r.subject_id === sub.id);
      const present = subRecords.filter(r => r.status === 'PRESENT').length;
      const total = subRecords.length || 1;
      const pct = AppUtils.calculateAttendancePercentage(present, total);

      return `
        <tr>
          <td>
            <div class="font-semibold">${sub.name}</div>
            <div class="text-muted" style="font-size:0.75rem;">${sub.subject_code}</div>
          </td>
          <td>${present} / ${total}</td>
          <td>
            <div class="flex items-center gap-2">
              <div style="flex:1; background:var(--border-color); height:8px; border-radius:4px; overflow:hidden;">
                <div style="width:${pct}%; background:${pct < 75 ? 'var(--danger)' : 'var(--success)'}; height:100%;"></div>
              </div>
              <span class="font-bold" style="font-size:0.85rem;">${pct}%</span>
            </div>
          </td>
          <td>
            ${pct < 75 ? '<span class="badge badge-danger">Low Attendance</span>' : '<span class="badge badge-success">Good</span>'}
          </td>
        </tr>
      `;
    }).join('');
  },

  renderStudentCorrections(myCorrections) {
    const container = document.getElementById('student-corrections-list');
    if (!container) return;

    if (!myCorrections || !myCorrections.length) {
      container.innerHTML = '<div class="text-muted">No correction requests submitted.</div>';
      return;
    }

    container.innerHTML = myCorrections.map(c => `
      <div class="card" style="margin-bottom:0.75rem; padding:1rem;">
        <div class="flex justify-between items-center">
          <div>
            <span class="font-bold">${c.subject_code}</span> • <span class="text-muted">${c.date}</span>
            <div class="text-secondary" style="font-size:0.85rem; margin-top:0.2rem;">"${c.reason}"</div>
          </div>
          <div>${AppUtils.renderStatusBadge(c.status)}</div>
        </div>
      </div>
    `).join('');
  }
};

window.DashboardModule = DashboardModule;
