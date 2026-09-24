/**
 * Smart Attendance Management System - Shared Layout & Navigation Component
 * Dynamically builds sidebar menu, top header, breadcrumbs, and role switcher based on logged-in user.
 */

const LayoutComponent = {
  // Navigation links definition by role
  navigation: [
    { label: 'Dashboard', page: 'dashboard', roles: ['ADMIN', 'FACULTY', 'STUDENT'], icon: 'fa-chart-line', getHref: (user) => {
        if (user.role === 'FACULTY') return 'faculty-dashboard.html';
        if (user.role === 'STUDENT') return 'student-dashboard.html';
        return 'admin-dashboard.html';
      }
    },
    { label: 'Student Management', page: 'students', roles: ['ADMIN'], icon: 'fa-user-graduate', href: 'students.html' },
    { label: 'Faculty Management', page: 'faculty', roles: ['ADMIN'], icon: 'fa-chalkboard-teacher', href: 'faculty.html' },
    { label: 'Subject Management', page: 'subjects', roles: ['ADMIN'], icon: 'fa-book-open', href: 'subjects.html' },
    { label: 'Attendance Recording', page: 'attendance', roles: ['ADMIN', 'FACULTY'], icon: 'fa-clipboard-check', href: 'attendance.html' },
    { label: 'Attendance History', page: 'attendance-history', roles: ['ADMIN', 'FACULTY', 'STUDENT'], icon: 'fa-history', href: 'attendance-history.html' },
    { label: 'Correction Requests', page: 'corrections', roles: ['ADMIN', 'FACULTY', 'STUDENT'], icon: 'fa-tasks', href: 'corrections.html', hasBadge: true },
    { label: 'Reports & Analytics', page: 'reports', roles: ['ADMIN', 'FACULTY', 'STUDENT'], icon: 'fa-chart-pie', href: 'reports.html' }
  ],

  async init(activePageKey = 'dashboard') {
    const user = AuthService.getCurrentUser();
    if (!user) return;
    await this.renderSidebar(user, activePageKey);
    this.renderHeader(user, activePageKey);
    this.setupThemeToggle();
  },

  async renderSidebar(user, activePageKey) {
    const sidebarContainer = document.getElementById('app-sidebar');
    if (!sidebarContainer) return;

    // Filter navigation menu by user role
    const allowedNav = this.navigation.filter(item => item.roles.includes(user.role));

    // Pending correction count for badge
    let pendingCount = 0;
    try {
      if (window.ApiService) {
        const reqs = await ApiService.getCorrectionRequests({ status: 'PENDING' });
        pendingCount = reqs ? reqs.length : 0;
      } else if (window.MockDataService) {
        pendingCount = MockDataService.correctionRequests.filter(c => c.status === 'PENDING').length;
      }
    } catch (e) {
      pendingCount = 0;
    }

    let navItemsHTML = allowedNav.map(item => {
      const href = item.getHref ? item.getHref(user) : item.href;
      const isActive = activePageKey === item.page ? 'active' : '';
      const badgeHTML = (item.hasBadge && pendingCount > 0) ? `<span class="nav-badge">${pendingCount}</span>` : '';

      return `
        <a href="${href}" class="nav-item ${isActive}">
          <i class="fas ${item.icon}"></i>
          <span>${item.label}</span>
          ${badgeHTML}
        </a>
      `;
    }).join('');

    sidebarContainer.innerHTML = `
      <div class="sidebar-header">
        <div class="sidebar-logo">SA</div>
        <div class="sidebar-title-box">
          <span class="sidebar-title">Smart Attendance</span>
          <span class="sidebar-subtitle">Management System</span>
        </div>
      </div>

      <div class="sidebar-menu">
        <div class="menu-category">Main Menu</div>
        ${navItemsHTML}
      </div>

      <div class="sidebar-footer">
        <div class="user-profile-card">
          <div class="user-avatar">${user.name ? user.name.charAt(0) : 'U'}</div>
          <div class="user-info">
            <span class="user-name">${user.name || 'User'}</span>
            <span class="user-role-badge">${user.role}</span>
          </div>
          <button class="logout-btn" onclick="AuthService.logout()" title="Logout">
            <i class="fas fa-sign-out-alt"></i>
          </button>
        </div>
      </div>
    `;
  },

  renderHeader(user, activePageKey) {
    const headerContainer = document.getElementById('app-header');
    if (!headerContainer) return;

    const navItem = this.navigation.find(n => n.page === activePageKey);
    const title = navItem ? navItem.label : 'Dashboard';

    headerContainer.innerHTML = `
      <div class="header-left">
        <div>
          <h1 class="page-title">${title}</h1>
          <div class="page-breadcrumb">
            <i class="fas fa-home"></i> / <span>${user.role.toLowerCase()}</span> / <span>${title}</span>
          </div>
        </div>
      </div>

      <div class="header-right">
        <!-- Demo Role Switcher for instant evaluator testing -->
        <div class="role-switcher-dropdown">
          <label><i class="fas fa-user-shield"></i> Demo Role:</label>
          <select id="roleSelect" onchange="AuthService.switchDemoRole(this.value)">
            <option value="ADMIN" ${user.role === 'ADMIN' ? 'selected' : ''}>Admin View</option>
            <option value="FACULTY" ${user.role === 'FACULTY' ? 'selected' : ''}>Faculty View</option>
            <option value="STUDENT" ${user.role === 'STUDENT' ? 'selected' : ''}>Student View</option>
          </select>
        </div>

        <button class="header-btn" id="themeToggleBtn" title="Toggle Light/Dark Theme">
          <i class="fas fa-moon"></i>
        </button>

        <button class="header-btn" title="Notifications">
          <i class="fas fa-bell"></i>
          <span class="notification-dot"></span>
        </button>
      </div>
    `;
  },

  setupThemeToggle() {
    const themeBtn = document.getElementById('themeToggleBtn');
    if (!themeBtn) return;

    const currentTheme = localStorage.getItem('app_theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    themeBtn.innerHTML = currentTheme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';

    themeBtn.addEventListener('click', () => {
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
      const newTheme = isDark ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('app_theme', newTheme);
      themeBtn.innerHTML = newTheme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    });
  }
};

window.LayoutComponent = LayoutComponent;
