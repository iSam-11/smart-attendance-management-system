/**
 * Smart Attendance Management System - Subject Management Controller
 */

const SubjectsModule = {
  async init() {
    AuthService.protectPage(['ADMIN']);
    LayoutComponent.init('subjects');

    await this.loadDepartmentFilterOptions();
    await this.renderSubjectsTable();
    this.setupEventListeners();
  },

  async loadDepartmentFilterOptions() {
    const departments = await ApiService.getDepartments();
    const deptSelect = document.getElementById('filterSubjectDept');
    const addDeptSelect = document.getElementById('addSubjectDept');

    if (deptSelect) {
      deptSelect.innerHTML = '<option value="">All Departments</option>' +
        departments.map(d => `<option value="${d.id}">${d.name} (${d.code})</option>`).join('');
    }
    if (addDeptSelect) {
      addDeptSelect.innerHTML = departments.map(d => `<option value="${d.id}">${d.name} (${d.code})</option>`).join('');
    }
  },

  async renderSubjectsTable() {
    const search = document.getElementById('searchSubject')?.value || '';
    const deptId = document.getElementById('filterSubjectDept')?.value || '';

    let subjects = await ApiService.getSubjects({ department_id: deptId });
    if (search) {
      const q = search.toLowerCase();
      subjects = subjects.filter(s => 
        s.name.toLowerCase().includes(q) ||
        s.subject_code.toLowerCase().includes(q)
      );
    }

    const tableBody = document.getElementById('subjectsTableBody');
    if (!tableBody) return;

    if (!subjects || !subjects.length) {
      tableBody.innerHTML = '<tr><td colspan="6" class="text-muted text-center" style="padding:2rem;">No subjects found.</td></tr>';
      return;
    }

    tableBody.innerHTML = subjects.map(s => `
      <tr>
        <td><span class="font-bold badge badge-info">${s.subject_code}</span></td>
        <td><div class="font-semibold">${s.name}</div></td>
        <td><span class="font-bold">${s.credits} Credits</span></td>
        <td><span class="badge badge-neutral">${s.department_code}</span></td>
        <td>${AppUtils.renderStatusBadge(s.is_active ? 'ACTIVE' : 'INACTIVE')}</td>
        <td>
          <div class="flex items-center gap-1">
            <button class="btn btn-sm btn-secondary" onclick="SubjectsModule.editSubject(${s.id})" title="Edit">
              <i class="fas fa-edit"></i>
            </button>
          </div>
        </td>
      </tr>
    `).join('');

    document.getElementById('totalSubjectsCount').textContent = subjects.length.toString();
  },

  setupEventListeners() {
    const searchInput = document.getElementById('searchSubject');
    const deptSelect = document.getElementById('filterSubjectDept');

    if (searchInput) searchInput.addEventListener('input', () => this.renderSubjectsTable());
    if (deptSelect) deptSelect.addEventListener('change', () => this.renderSubjectsTable());

    const addForm = document.getElementById('addSubjectForm');
    if (addForm) {
      addForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await this.handleCreateSubject();
      });
    }
  },

  async handleCreateSubject() {
    const code = document.getElementById('addSubjectCode').value;
    const name = document.getElementById('addSubjectName').value;
    const credits = document.getElementById('addSubjectCredits').value;
    const deptId = document.getElementById('addSubjectDept').value;

    const deptObj = (await ApiService.getDepartments()).find(d => d.id == deptId);

    try {
      await ApiService.addSubject({
        subject_code: code,
        name: name,
        credits: parseInt(credits),
        department_id: parseInt(deptId),
        department_code: deptObj ? deptObj.code : 'CSE'
      });

      AppUtils.showToast(`Subject ${code} - ${name} added successfully!`, 'success');
      AppUtils.closeModal('addSubjectModal');
      document.getElementById('addSubjectForm').reset();
      await this.renderSubjectsTable();
    } catch (err) {
      AppUtils.showToast(err.message, 'danger');
    }
  },

  editSubject(subjectId) {
    AppUtils.showToast(`Edit Subject #${subjectId}`, 'info');
  }
};

window.SubjectsModule = SubjectsModule;
