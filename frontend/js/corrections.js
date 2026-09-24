/**
 * Smart Attendance Management System - Correction Requests Controller
 */

const CorrectionsModule = {
  currentTabStatus: '',
  selectedRequestId: null,

  async init() {
    AuthService.protectPage(['ADMIN', 'FACULTY', 'STUDENT']);
    LayoutComponent.init('corrections');

    const user = AuthService.getCurrentUser();
    
    // Hide "New Correction Request" button if user is Admin/Faculty, show for Student
    const newReqBtn = document.getElementById('newCorrectionBtn');
    if (newReqBtn) {
      newReqBtn.style.display = user.role === 'STUDENT' ? 'inline-flex' : 'none';
    }

    await this.renderCorrectionsTable();
    this.setupEventListeners();
  },

  async renderCorrectionsTable() {
    const user = AuthService.getCurrentUser();
    const filters = {};
    if (this.currentTabStatus) {
      filters.status = this.currentTabStatus;
    }
    if (user.role === 'STUDENT') {
      filters.student_id = user.id;
    }

    const requests = await ApiService.getCorrectionRequests(filters);
    const tableBody = document.getElementById('correctionsTableBody');
    if (!tableBody) return;

    if (!requests || !requests.length) {
      tableBody.innerHTML = '<tr><td colspan="7" class="text-muted text-center" style="padding:2.5rem;">No correction requests found.</td></tr>';
      return;
    }

    tableBody.innerHTML = requests.map(c => `
      <tr>
        <td><span class="font-bold">#REQ-${c.id}</span></td>
        <td>
          <div class="font-semibold">${c.student_name}</div>
          <div class="text-muted" style="font-size:0.75rem;">Roll: ${c.roll_number}</div>
        </td>
        <td>
          <div class="font-semibold">${c.subject_code}</div>
          <div class="text-muted" style="font-size:0.75rem;">Date: ${c.date}</div>
        </td>
        <td>
          <div class="flex items-center gap-1">
            ${AppUtils.renderStatusBadge(c.current_status)}
            <i class="fas fa-arrow-right text-muted" style="font-size:0.75rem;"></i>
            ${AppUtils.renderStatusBadge(c.requested_status)}
          </div>
        </td>
        <td><span class="text-secondary" style="font-size:0.85rem;">"${c.reason}"</span></td>
        <td>${AppUtils.renderStatusBadge(c.status)}</td>
        <td>
          ${user.role !== 'STUDENT' && c.status === 'PENDING' ? `
            <button class="btn btn-sm btn-primary" onclick="CorrectionsModule.openReviewModal(${c.id})">
              <i class="fas fa-gavel"></i> Review
            </button>
          ` : `
            <span class="text-muted" style="font-size:0.75rem;">
              ${c.reviewed_by ? `Reviewed by ${c.reviewed_by}` : 'Awaiting Review'}
            </span>
          `}
        </td>
      </tr>
    `).join('');
  },

  setupEventListeners() {
    // Tab switching
    const tabItems = document.querySelectorAll('.tab-item');
    tabItems.forEach(tab => {
      tab.addEventListener('click', (e) => {
        tabItems.forEach(t => t.classList.remove('active'));
        e.target.classList.add('active');
        this.currentTabStatus = e.target.getAttribute('data-status') || '';
        this.renderCorrectionsTable();
      });
    });

    // New Correction Request Modal setup for Student
    const newReqBtn = document.getElementById('newCorrectionBtn');
    if (newReqBtn) {
      newReqBtn.addEventListener('click', () => this.openNewRequestModal());
    }

    const newReqForm = document.getElementById('newCorrectionForm');
    if (newReqForm) {
      newReqForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await this.handleCreateRequest();
      });
    }

    // Review Request Form submission for Faculty/Admin
    const reviewForm = document.getElementById('reviewCorrectionForm');
    if (reviewForm) {
      reviewForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await this.handleReviewSubmit();
      });
    }
  },

  async openNewRequestModal() {
    const user = AuthService.getCurrentUser();
    const records = await ApiService.getAttendanceRecords({ student_id: user.id, status: 'ABSENT' });

    const recSelect = document.getElementById('correctionRecordSelect');
    if (recSelect) {
      if (!records || !records.length) {
        recSelect.innerHTML = '<option value="">No Absent records available to request correction</option>';
      } else {
        recSelect.innerHTML = records.map(r => 
          `<option value="${r.id}" data-date="${r.attendance_date}" data-subject="${r.subject_code}" data-status="${r.status}">
            ${r.attendance_date} - ${r.subject_code} (${r.subject_name})
          </option>`
        ).join('');
      }
    }

    AppUtils.openModal('newCorrectionModal');
  },

  async handleCreateRequest() {
    const user = AuthService.getCurrentUser();
    const recSelect = document.getElementById('correctionRecordSelect');
    const reason = document.getElementById('correctionReasonInput').value;

    if (!recSelect.value) {
      AppUtils.showToast('Please select a valid attendance record!', 'warning');
      return;
    }

    const selectedOpt = recSelect.options[recSelect.selectedIndex];

    try {
      await ApiService.createCorrectionRequest({
        attendance_id: parseInt(recSelect.value),
        student_id: user.id,
        student_name: user.name,
        roll_number: user.roll || '24CSE001',
        subject_code: selectedOpt.getAttribute('data-subject') || 'CS501',
        date: selectedOpt.getAttribute('data-date') || new Date().toISOString().split('T')[0],
        current_status: selectedOpt.getAttribute('data-status') || 'ABSENT',
        requested_status: 'PRESENT',
        reason: reason
      });

      AppUtils.showToast('Correction request submitted successfully!', 'success');
      AppUtils.closeModal('newCorrectionModal');
      document.getElementById('newCorrectionForm').reset();
      await this.renderCorrectionsTable();
    } catch (err) {
      AppUtils.showToast(err.message, 'danger');
    }
  },

  async openReviewModal(requestId) {
    this.selectedRequestId = requestId;
    const requests = await ApiService.getCorrectionRequests();
    const req = requests.find(r => r.id === requestId);
    if (!req) return;

    document.getElementById('reviewReqStudentName').textContent = `${req.student_name} (${req.roll_number})`;
    document.getElementById('reviewReqSubjectDate').textContent = `${req.subject_code} • ${req.date}`;
    document.getElementById('reviewReqReason').textContent = `"${req.reason}"`;

    AppUtils.openModal('reviewCorrectionModal');
  },

  async handleReviewSubmit(actionStatus = 'APPROVED') {
    if (!this.selectedRequestId) return;
    const comment = document.getElementById('reviewCommentInput').value;
    const user = AuthService.getCurrentUser();

    try {
      await ApiService.reviewCorrectionRequest(
        this.selectedRequestId,
        actionStatus,
        comment,
        user.name
      );

      AppUtils.showToast(`Correction request ${actionStatus.toLowerCase()}!`, actionStatus === 'APPROVED' ? 'success' : 'warning');
      AppUtils.closeModal('reviewCorrectionModal');
      document.getElementById('reviewCorrectionForm').reset();
      await this.renderCorrectionsTable();
    } catch (err) {
      AppUtils.showToast(err.message, 'danger');
    }
  }
};

window.CorrectionsModule = CorrectionsModule;
