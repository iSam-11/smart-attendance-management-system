/**
 * Smart Attendance Management System - Student Management Controller
 */

const StudentsModule = {
  async init() {
    AuthService.protectPage(['ADMIN']);
    LayoutComponent.init('students');
    
    await this.loadDepartmentFilterOptions();
    await this.renderStudentsTable();
    this.setupEventListeners();
  },

  async loadDepartmentFilterOptions() {
    const departments = await ApiService.getDepartments();
    const deptSelect = document.getElementById('filterDepartment');
    const addDeptSelect = document.getElementById('addStudentDept');

    if (deptSelect) {
      deptSelect.innerHTML = '<option value="">All Departments</option>' +
        departments.map(d => `<option value="${d.id}">${d.name} (${d.code})</option>`).join('');
    }
    if (addDeptSelect) {
      addDeptSelect.innerHTML = departments.map(d => `<option value="${d.id}">${d.name} (${d.code})</option>`).join('');
    }
  },

  async renderStudentsTable() {
    const search = document.getElementById('searchStudent')?.value || '';
    const deptId = document.getElementById('filterDepartment')?.value || '';
    const lowOnly = document.getElementById('filterLowAttendance')?.checked || false;

    const students = await ApiService.getStudents({
      search,
      department_id: deptId,
      low_attendance_only: lowOnly
    });

    const tableBody = document.getElementById('studentsTableBody');
    if (!tableBody) return;

    if (!students || !students.length) {
      tableBody.innerHTML = '<tr><td colspan="8" class="text-muted text-center" style="padding:2rem;">No students found matching filters.</td></tr>';
      return;
    }

    tableBody.innerHTML = students.map(s => `
      <tr>
        <td><span class="font-bold">${s.roll_number}</span></td>
        <td>
          <div class="font-semibold">${s.first_name} ${s.last_name}</div>
          <div class="text-muted" style="font-size:0.75rem;">${s.email}</div>
        </td>
        <td><span class="badge badge-neutral">${s.department_code}</span></td>
        <td>${s.section_name || 'Section A'}</td>
        <td>${s.admission_year}</td>
        <td>
          <span class="font-bold ${s.overall_attendance < 75 ? 'text-danger' : 'text-success'}">
            ${s.overall_attendance}%
          </span>
        </td>
        <td>${AppUtils.renderStatusBadge(s.is_active ? 'ACTIVE' : 'INACTIVE')}</td>
        <td>
          <div class="flex items-center gap-1">
            <button class="btn btn-sm btn-secondary" onclick="StudentsModule.viewStudentDetails(${s.id})" title="View Details">
              <i class="fas fa-eye"></i>
            </button>
            <button class="btn btn-sm btn-secondary" onclick="StudentsModule.editStudent(${s.id})" title="Edit">
              <i class="fas fa-edit"></i>
            </button>
          </div>
        </td>
      </tr>
    `).join('');

    document.getElementById('totalStudentsCount').textContent = students.length.toString();
  },

  setupEventListeners() {
    const searchInput = document.getElementById('searchStudent');
    const deptSelect = document.getElementById('filterDepartment');
    const lowCheckbox = document.getElementById('filterLowAttendance');

    if (searchInput) searchInput.addEventListener('input', () => this.renderStudentsTable());
    if (deptSelect) deptSelect.addEventListener('change', () => this.renderStudentsTable());
    if (lowCheckbox) lowCheckbox.addEventListener('change', () => this.renderStudentsTable());

    const addForm = document.getElementById('addStudentForm');
    if (addForm) {
      addForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await this.handleCreateStudent();
      });
    }
  },

  async handleCreateStudent() {
    const firstName = document.getElementById('addStudentFirstName').value;
    const lastName = document.getElementById('addStudentLastName').value;
    const rollNumber = document.getElementById('addStudentRoll').value;
    const email = document.getElementById('addStudentEmail').value;
    const deptId = document.getElementById('addStudentDept').value;
    const year = document.getElementById('addStudentYear').value;

    const deptObj = (await ApiService.getDepartments()).find(d => d.id == deptId);

    try {
      await ApiService.addStudent({
        first_name: firstName,
        last_name: lastName,
        roll_number: rollNumber,
        email: email,
        department_id: parseInt(deptId),
        department_code: deptObj ? deptObj.code : 'CSE',
        section_id: 1,
        section_name: 'Section A',
        admission_year: parseInt(year)
      });

      AppUtils.showToast(`Student ${firstName} ${lastName} added successfully!`, 'success');
      AppUtils.closeModal('addStudentModal');
      document.getElementById('addStudentForm').reset();
      await this.renderStudentsTable();
    } catch (err) {
      AppUtils.showToast(err.message, 'danger');
    }
  },

  async viewStudentDetails(studentId) {
    const student = (await ApiService.getStudents()).find(s => s.id === studentId);
    if (!student) return;

    alert(`Student Summary:\nName: ${student.first_name} ${student.last_name}\nRoll No: ${student.roll_number}\nDept: ${student.department_code}\nAttendance: ${student.overall_attendance}%`);
  },

  editStudent(studentId) {
    AppUtils.showToast(`Edit feature opened for Student #${studentId}`, 'info');
  }
};

window.StudentsModule = StudentsModule;
