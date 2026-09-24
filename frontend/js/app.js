/**
 * Smart Attendance Management System - Core App Utilities & UI Controllers
 */

const AppUtils = {
  // Toast Notification Controller
  showToast(message, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let iconClass = 'fa-info-circle';
    if (type === 'success') iconClass = 'fa-check-circle';
    if (type === 'danger') iconClass = 'fa-exclamation-circle';
    if (type === 'warning') iconClass = 'fa-exclamation-triangle';

    toast.innerHTML = `
      <i class="fas ${iconClass} toast-icon"></i>
      <span class="toast-message">${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(20px)';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  },

  // Modal Open/Close Helper
  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('active');
    }
  },

  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('active');
    }
  },

  // Calculate attendance percentage formula per REQUIREMENTS.md
  // Attendance Percentage = (Present Classes / Conducted Classes) * 100
  calculateAttendancePercentage(presentCount, totalConducted) {
    if (!totalConducted || totalConducted === 0) return 100.0;
    return parseFloat(((presentCount / totalConducted) * 100).toFixed(1));
  },

  // Render Status Badge HTML
  renderStatusBadge(status) {
    const s = (status || '').toUpperCase();
    if (s === 'PRESENT' || s === 'APPROVED' || s === 'ACTIVE') {
      return `<span class="badge badge-success"><i class="fas fa-check"></i> ${s}</span>`;
    }
    if (s === 'ABSENT' || s === 'REJECTED' || s === 'INACTIVE') {
      return `<span class="badge badge-danger"><i class="fas fa-times"></i> ${s}</span>`;
    }
    if (s === 'PENDING') {
      return `<span class="badge badge-warning"><i class="fas fa-clock"></i> PENDING</span>`;
    }
    return `<span class="badge badge-neutral">${s}</span>`;
  },

  // Format Date String
  formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  },

  // CSV Export Utility
  exportToCSV(filename, rows) {
    if (!rows || !rows.length) return;

    const separator = ',';
    const keys = Object.keys(rows[0]);
    const csvContent =
      keys.join(separator) +
      '\n' +
      rows.map(row => {
        return keys.map(k => {
          let cell = row[k] === null || row[k] === undefined ? '' : row[k];
          cell = cell.toString().replace(/"/g, '""');
          if (cell.search(/("|,|\n)/g) >= 0) {
            cell = `"${cell}"`;
          }
          return cell;
        }).join(separator);
      }).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    if (link.download !== undefined) {
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', filename);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  }
};

window.AppUtils = AppUtils;
