/**
 * Empower Frontend - Constants
 */

export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login.html',
  SIGNUP: '/signup.html',
  PROJECTS: '/projects.html',
  STORIES: '/stories.html',
  ABOUT: '/about.html',
  CONTACT: '/contact.html',
  DONATE: '/donate.html',
  SUPPORT: '/support.html'
};

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  SERVER_ERROR: 500
};

export const LOCAL_STORAGE_KEYS = {
  TOKEN: 'token',
  USER: 'user',
  THEME: 'theme',
  LANGUAGE: 'language'
};
