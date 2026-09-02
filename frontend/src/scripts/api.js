/**
 * Empower Frontend - API Module
 * Handles all API communication with the backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

/**
 * Generic API request handler.
 * Ensures payloads match the FastAPI backend contracts.
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  const token = localStorage.getItem('token');
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login.html';
      return null;
    }

    const contentType = response.headers.get('content-type') || '';
    const data = contentType.includes('application/json') ? await response.json() : await response.text();

    if (!response.ok) {
      throw new Error(typeof data === 'object' && data && 'detail' in data ? data.detail : 'API Error');
    }

    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// Auth Endpoints
export async function login(username, password) {
  return apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password })
  });
}

export async function signup(username, email, password) {
  return apiRequest('/auth/signup', {
    method: 'POST',
    body: JSON.stringify({ username, email, password })
  });
}

// Health Check
export async function healthCheck() {
  return apiRequest('/health');
}

// Projects Endpoints
export async function getProjects() {
  return apiRequest('/projects');
}

export async function getProject(id) {
  return apiRequest(`/projects/${id}`);
}

export async function createProject(name, category, summary, description) {
  return apiRequest('/projects', {
    method: 'POST',
    body: JSON.stringify({ name, category, summary, description })
  });
}

// Stories Endpoints
export async function getStories() {
  return apiRequest('/stories');
}

export async function getStory(id) {
  return apiRequest(`/stories/${id}`);
}

export async function createStory(title, category, excerpt, year) {
  return apiRequest('/stories', {
    method: 'POST',
    body: JSON.stringify({ title, category, excerpt, year })
  });
}

// Contact Endpoints
export async function submitContact(name, email, message) {
  return apiRequest('/contact', {
    method: 'POST',
    body: JSON.stringify({ name, email, message })
  });
}
