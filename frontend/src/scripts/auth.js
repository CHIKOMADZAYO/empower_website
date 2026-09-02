/**
 * Empower Frontend - Authentication Module
 */

/**
 * Set authentication token
 */
export function setToken(token) {
  localStorage.setItem('token', token);
}

/**
 * Get authentication token
 */
export function getToken() {
  return localStorage.getItem('token');
}

/**
 * Remove authentication token (logout)
 */
export function clearToken() {
  localStorage.removeItem('token');
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated() {
  return !!getToken();
}

/**
 * Redirect to login if not authenticated
 */
export function requireAuth() {
  if (!isAuthenticated()) {
    window.location.href = '/login.html';
  }
}

/**
 * Decode JWT token (simple implementation)
 */
export function decodeToken(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Token decode error:', error);
    return null;
  }
}
