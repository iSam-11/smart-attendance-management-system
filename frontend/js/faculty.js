/**
 * Smart Attendance Management System - Faculty Management Controller
 */

const FacultyModule = {
  async init() {
    AuthService.protectPage(['ADMIN']);
    LayoutComponent.init('faculty');

    await this.loadDepartmentFilterOptions();
    await this.renderFacultyTable();
    this.setupEventListeners();
  },

  async loadDepartmentFilterOptions() {
    const departments = await ApiService.getDepartments();
    const deptSelect = document.getElementById('filterFacultyDept');
    const addDeptSelect = document.getElementById('addFacultyDept');

    if (deptSelect) {
      deptSelect.innerHTML = '<option value="">All Departments</option>' +
        departments.map(d => `<option value="${d.id}">${d.name} (${d.code})</option>`).join('');
    }
    if (addDeptSelect) {
      addDeptSelect.innerHTML = departments.map(d => `<option value="${d.id}">${d.name} (${d.code})</option>`).join('');
    }
  },

  async renderFacultyTable() {
    const search = document.getElementById('searchFaculty')?.value || '';
    const deptId = document.getElementById('filterFacultyDept')?.value || '';

    let facultyList = await ApiService.getFaculty({ department_id: deptId });
    if (search) {
      const q = search.toLowerCase();
      facultyList = facultyList.filter(f => 
        (f.first_name || '').toLowerCase().includes(q) ||
        (f.last_name || '').toLowerCase().includes(q) ||
        (f.employee_identifier || '').toLowerCase().includes(q)
      );
    }

    const tableBody = document.getElementById('facultyTableBody');
    if (!tableBody) return;

    if (!facultyList || !facultyList.length) {
      tableBody.innerHTML = '<tr><td colspan="7" class="text-muted text-center" style="padding:2rem;">No faculty members found.</td></tr>';
      return;
    }

    const subjects = await ApiService.getSubjects();

    tableBody.innerHTML = facultyList.map(f => {
      const assignedSubjectNames = f.assigned_subjects
        ? f.assigned_subjects.map(id => subjects.find(s => s.id === id)?.subject_code || `SUBJ-${id}`).join(', ')
        : 'None';

      return `
        <tr>
          <td><span class="font-bold">${f.employee_identifier}</span></td>
          <td>
            <div class="font-semibold">${f.first_name} ${f.last_name}</div>
            <div class="text-muted" style="font-size:0.75rem;">${f.email}</div>
          </td>
          <td><span class="badge badge-neutral">${f.department_code}</span></td>
          <td><span class="badge badge-info">${assignedSubjectNames}</span></td>
          <td>Section A, Section B</td>
          <td>${AppUtils.renderStatusBadge(f.is_active ? 'ACTIVE' : 'INACTIVE')}</td>
          <td>
            <div class="flex items-center gap-1">
              <button class="btn btn-sm btn-secondary" onclick="FacultyModule.openAssignModal(${f.id})" title="Assign Classes">
                <i class="fas fa-link"></i> Assign
              </button>
              <button class="btn btn-sm btn-secondary" onclick="FacultyModule.editFaculty(${f.id})" title="Edit">
                <i class="fas fa-edit"></i>
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join('');

    document.getElementById('totalFacultyCount').textContent = facultyList.length.toString();
  },

  setupEventListeners() {
    const searchInput = document.getElementById('searchFaculty');
    const deptSelect = document.getElementById('filterFacultyDept');

    if (searchInput) searchInput.addEventListener('input', () => this.renderFacultyTable());
    if (deptSelect) deptSelect.addEventListener('change', () => this.renderFacultyTable());

    const addForm = document.getElementById('addFacultyForm');
    if (addForm) {
      addForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await this.handleCreateFaculty();
      });
    }
  },

  async handleCreateFaculty() {
    const firstName = document.getElementById('addFacultyFirstName').value;
    const lastName = document.getElementById('addFacultyLastName').value;
    const email = document.getElementById('addFacultyEmail').value;
    const deptId = document.getElementById('addFacultyDept').value;

    const deptObj = (await ApiService.getDepartments()).find(d => d.id == deptId);

    try {
      await ApiService.addFaculty({
        first_name: firstName,
        last_name: lastName,
        email: email,
        department_id: parseInt(deptId),
        department_code: deptObj ? deptObj.code : 'CSE',
        assigned_subjects: [1],
        assigned_sections: [1]
      });

      AppUtils.showToast(`Faculty ${firstName} ${lastName} added successfully!`, 'success');
      AppUtils.closeModal('addFacultyModal');
      document.getElementById('addFacultyForm').reset();
      await this.renderFacultyTable();
    } catch (err) {
      AppUtils.showToast(err.message, 'danger');
    }
  },

  openAssignModal(facultyId) {
    AppUtils.showToast(`Assign Subject/Section modal opened for Faculty #${facultyId}`, 'info');
  },

  editFaculty(facultyId) {
    AppUtils.showToast(`Edit Faculty #${facultyId}`, 'info');
  }
};

window.FacultyModule = FacultyModule;
