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

function setupNavigation() {
  const navigation = document.querySelector('.navbar');
  const menu = navigation?.querySelector('ul');
  if (!navigation || !menu) return;

  const toggle = document.createElement('button');
  toggle.className = 'nav-toggle';
  toggle.type = 'button';
  toggle.setAttribute('aria-expanded', 'false');
  toggle.setAttribute('aria-controls', 'primary-navigation');
  toggle.setAttribute('aria-label', 'Open navigation menu');
  toggle.innerHTML = '<span></span><span></span><span></span>';
  menu.id = 'primary-navigation';
  navigation.insertBefore(toggle, menu);

  toggle.addEventListener('click', () => {
    const isOpen = navigation.classList.toggle('nav-open');
    toggle.setAttribute('aria-expanded', String(isOpen));
    toggle.setAttribute('aria-label', isOpen ? 'Close navigation menu' : 'Open navigation menu');
  });
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
  setupNavigation();
  console.log('Empower Frontend Ready');
});
