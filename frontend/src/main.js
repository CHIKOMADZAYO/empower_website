/**
 * Empower Frontend - Main Entry Point
 */

console.log('Empower Frontend Loaded');

// Import styles
import './styles/index.css';
import './styles/main.css';

// Import utilities and make available globally
import * as API from './scripts/api.js';
import * as Auth from './scripts/auth.js';
import * as Utils from './pages/utils.js';
import * as Constants from './scripts/constants.js';

// Export for use in pages
window.API = API;
window.Auth = Auth;
window.Utils = Utils;
window.Constants = Constants;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
  console.log('Empower Frontend Ready');
});
