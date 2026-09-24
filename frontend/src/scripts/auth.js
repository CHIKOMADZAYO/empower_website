/**
 * Empower Frontend - Authentication Module
 */

import { getProfile, login, signup } from './api.js';

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

export function setStoredUser(user) {
  if (user) localStorage.setItem('user', JSON.stringify(user));
}

export function getStoredUser() {
  try {
    const raw = localStorage.getItem('user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function logout(redirect = '/login.html') {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.location.href = redirect;
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

export async function requireRole(allowedRoles, redirect = '/login.html') {
  requireAuth();
  if (!allowedRoles || allowedRoles.length === 0) return getStoredUser();
  try {
    const profile = await getProfile();
    const user = profile?.user ?? profile;
    if (user) setStoredUser(user);
    if (!user || !allowedRoles.includes(user.role)) {
      window.location.href = redirect;
      return null;
    }
    return user;
  } catch {
    window.location.href = redirect;
    return null;
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

/**
 * Decide where to send a user after login/signup based on JWT role.
 */
export function dashboardForRole(role) {
  if (role === 'admin') return 'admin.html';
  return 'dashboard.html';
}

function setFormStatus(selector, message, isError = false) {
  const status = document.querySelector(selector);
  if (!status) return;

  status.textContent = message;
  status.style.color = isError ? '#b42318' : '#0f766e';
}

async function finishAuth(response, statusSelector) {
  const token = response?.access_token;
  if (!token) throw new Error('No access token received');
  setToken(token);

  let role = decodeToken(token)?.role;
  try {
    const profile = await getProfile();
    const user = profile?.user ?? null;
    if (user) {
      setStoredUser(user);
      role = user.role;
    }
  } catch {
    // fall back to JWT role
  }

  setFormStatus(statusSelector, 'Signed in successfully. Redirecting...');
  window.location.href = dashboardForRole(role);
}

export async function handleLoginSubmit(event) {
  event.preventDefault();

  const form = event.currentTarget;
  const username = form.querySelector('#username')?.value.trim();
  const password = form.querySelector('#password')?.value;

  if (!username || !password) {
    setFormStatus('[data-login-status]', 'Please enter your username and password.', true);
    return;
  }

  try {
    setFormStatus('[data-login-status]', 'Signing in...');
    const response = await login(username, password);
    await finishAuth(response, '[data-login-status]');
  } catch (error) {
    setFormStatus('[data-login-status]', error.message || 'Unable to sign in. Please try again.', true);
  }
}

export async function handleSignupSubmit(event) {
  event.preventDefault();

  const form = event.currentTarget;
  const username = form.querySelector('#signup-username')?.value.trim();
  const email = form.querySelector('#signup-email')?.value.trim();
  const password = form.querySelector('#signup-password')?.value;
  const confirmPassword = form.querySelector('#signup-confirm-password')?.value;

  if (!username || !email || !password) {
    setFormStatus('[data-signup-status]', 'Please complete all fields.', true);
    return;
  }

  if (password !== confirmPassword) {
    setFormStatus('[data-signup-status]', 'Passwords do not match.', true);
    return;
  }

  try {
    setFormStatus('[data-signup-status]', 'Creating your account...');
    const response = await signup(username, email, password);
    await finishAuth(response, '[data-signup-status]');
  } catch (error) {
    setFormStatus('[data-signup-status]', error.message || 'Unable to create account. Please try again.', true);
  }
}

export function bindAuthForms() {
  const loginForm = document.querySelector('[data-login-form]');
  if (loginForm) {
    loginForm.addEventListener('submit', handleLoginSubmit);
  }

  const signupForm = document.querySelector('[data-signup-form]');
  if (signupForm) {
    signupForm.addEventListener('submit', handleSignupSubmit);
  }

  document.querySelectorAll('[data-logout]').forEach((button) => {
    button.addEventListener('click', (event) => {
      event.preventDefault();
      logout();
    });
  });
}

if (typeof window !== 'undefined') {
  window.addEventListener('DOMContentLoaded', bindAuthForms);
}

