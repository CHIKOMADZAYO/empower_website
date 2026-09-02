/**
 * Empower Frontend - Authentication Module
 */

import { login, signup } from './api.js';

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

function setFormStatus(selector, message, isError = false) {
  const status = document.querySelector(selector);
  if (!status) return;

  status.textContent = message;
  status.style.color = isError ? '#b42318' : '#0f766e';
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
    const token = response?.access_token;

    if (!token) {
      throw new Error('No access token received');
    }

    setToken(token);
    setFormStatus('[data-login-status]', 'Signed in successfully. Redirecting...');
    window.location.href = 'projects.html';
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
    const token = response?.access_token;

    if (!token) {
      throw new Error('No access token received');
    }

    setToken(token);
    setFormStatus('[data-signup-status]', 'Account created successfully. Redirecting...');
    window.location.href = 'projects.html';
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
}

if (typeof window !== 'undefined') {
  window.addEventListener('DOMContentLoaded', bindAuthForms);
}
