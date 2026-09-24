/**
 * Smart Attendance Management System - Auth & Session Manager
 * Handles authentication, user roles, permission validation, and token storage.
 */

const AuthService = {
  // Key names in LocalStorage
  TOKEN_KEY: 'attendance_token',
  USER_KEY: 'attendance_user',

  // Save session on successful login
  setSession(token, user) {
    localStorage.setItem(this.TOKEN_KEY, token);
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
  },

  // Clear session on logout
  logout() {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    const loginPath = window.location.pathname.includes('/pages/') ? 'login.html' : 'pages/login.html';
    window.location.href = loginPath;
  },

  // Get token
  getToken() {
    return localStorage.getItem(this.TOKEN_KEY);
  },

  // Get current logged-in user details
  getCurrentUser() {
    const userData = localStorage.getItem(this.USER_KEY);
    if (!userData) {
      return null;
    }
    try {
      return JSON.parse(userData);
    } catch (e) {
      return null;
    }
  },

  // Check if logged in
  isAuthenticated() {
    return !!this.getToken();
  },

  // Check user role
  hasRole(role) {
    const user = this.getCurrentUser();
    return user && user.role === role.toUpperCase();
  },

  // Switch demo role easily for quick testing
  switchDemoRole(newRole) {
    let mockUser = { id: 1, name: 'System Admin', role: 'ADMIN', email: 'admin@college.edu' };
    let redirectUrl = window.location.pathname.includes('/pages/') ? 'admin-dashboard.html' : 'pages/admin-dashboard.html';

    if (newRole === 'FACULTY') {
      mockUser = { id: 1, name: 'Dr. Rajesh Sharma', role: 'FACULTY', email: 'rajesh.sharma@college.edu', department: 'CSE' };
      redirectUrl = window.location.pathname.includes('/pages/') ? 'faculty-dashboard.html' : 'pages/faculty-dashboard.html';
    } else if (newRole === 'STUDENT') {
      mockUser = { id: 101, name: 'Aarav Mehta', role: 'STUDENT', email: 'aarav.m@student.college.edu', roll: '24CSE001' };
      redirectUrl = window.location.pathname.includes('/pages/') ? 'student-dashboard.html' : 'pages/student-dashboard.html';
    }

    const token = 'mock_jwt_token_' + btoa(JSON.stringify({ role: newRole, exp: Date.now() + 3600000 }));
    this.setSession(token, mockUser);
    
    // Redirect to relevant dashboard
    window.location.href = redirectUrl;
  },

  // Page level protection guard
  protectPage(allowedRoles = []) {
    const isLoginPage = window.location.pathname.includes('login.html');
    if (!this.isAuthenticated() && !isLoginPage) {
      console.warn('[AuthService] User not authenticated. Redirecting to login.');
      const loginPath = window.location.pathname.includes('/pages/') ? 'login.html' : 'pages/login.html';
      window.location.href = loginPath;
      return false;
    }

    if (allowedRoles.length > 0) {
      const user = this.getCurrentUser();
      if (!user || !allowedRoles.includes(user.role)) {
        console.warn(`[AuthService] User role '${user?.role}' not allowed for page.`);
        // Redirect to appropriate role dashboard
        let dest = 'admin-dashboard.html';
        if (user?.role === 'STUDENT') dest = 'student-dashboard.html';
        else if (user?.role === 'FACULTY') dest = 'faculty-dashboard.html';

        if (!window.location.pathname.includes('/pages/')) {
          dest = `pages/${dest}`;
        }
        window.location.href = dest;
        return false;
      }
    }
    return true;
  }
};

window.AuthService = AuthService;
