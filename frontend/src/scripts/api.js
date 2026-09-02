/**
 * Empower Frontend - API Module
 * Handles all API communication with the backend
 */

const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000/api/v1';

/**
 * Generic API request handler
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };

  // Add auth token if available
  const token = localStorage.getItem('token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers
    });

    if (response.status === 401) {
      // Handle unauthorized - clear token and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login.html';
    }

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'API Error');
    }

    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// Auth Endpoints
export async function login(email, password) {
  return apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password })
  });
}

export async function signup(email, password, fullName) {
  return apiRequest('/auth/signup', {
    method: 'POST',
    body: JSON.stringify({ email, password, full_name: fullName })
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

export async function createProject(title, description) {
  return apiRequest('/projects', {
    method: 'POST',
    body: JSON.stringify({ title, description })
  });
}

// Stories Endpoints
export async function getStories() {
  return apiRequest('/stories');
}

export async function getStory(id) {
  return apiRequest(`/stories/${id}`);
}

export async function createStory(title, content, projectId) {
  return apiRequest('/stories', {
    method: 'POST',
    body: JSON.stringify({ title, content, project_id: projectId })
  });
}

// Contact Endpoints
export async function submitContact(name, email, message) {
  return apiRequest('/contact', {
    method: 'POST',
    body: JSON.stringify({ name, email, message })
  });
}
