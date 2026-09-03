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

const pageName = window.location.pathname.split('/').pop().replace('.html', '') || 'index';
document.body.classList.add(`page-${pageName === 'index' ? 'home' : pageName}`);

function setupNavigation() {
  const navigation = document.querySelector('.navbar');
  const menu = navigation?.querySelector('ul');
  if (!navigation || !menu) return;

  const utilityBar = document.createElement('div');
  utilityBar.className = 'utility-bar';
  utilityBar.innerHTML = `
    <div class="utility-bar-inner">
      <div class="utility-links">
        <a href="https://wa.me/254700000000" target="_blank" rel="noreferrer" aria-label="WhatsApp" title="WhatsApp">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.5 3.5A11.8 11.8 0 0 0 12.1 0C5.6 0 .3 5.3.3 11.8c0 2.1.5 4.1 1.6 5.9L.2 24l6.5-1.7a11.8 11.8 0 0 0 5.4 1.3h.1c6.5 0 11.8-5.3 11.8-11.8 0-3.1-1.3-6.1-3.5-8.3Zm-8.4 18.1h-.1c-1.7 0-3.4-.5-4.8-1.3l-.3-.2-3.8 1 1-3.7-.2-.3a9.8 9.8 0 0 1-1.5-5.2C2.4 6.4 6.8 2 12.1 2c2.6 0 5.1 1 7 2.9a9.8 9.8 0 0 1 2.9 7c0 5.4-4.5 9.7-9.9 9.7Zm5.4-7.3c-.3-.2-1.7-.9-2-.9-.3-.1-.5-.1-.7.2l-1 1.2c-.2.2-.4.2-.7.1-2-.9-3.3-1.6-4.6-3.7-.3-.5.3-.4.8-1.4.1-.2.1-.4 0-.6l-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4-.3.3-1.2 1.1-1.2 2.7s1.2 3.1 1.4 3.3c.2.2 2.4 3.7 5.8 5.1 2.1.9 2.9 1 3.9.8.6-.1 1.7-.7 2-1.4.2-.7.2-1.3.1-1.4-.1-.2-.4-.3-.7-.5Z"/></svg>
        </a>
        <a href="https://www.facebook.com/" target="_blank" rel="noreferrer" aria-label="Facebook" title="Facebook">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 8h3V4h-3c-3.3 0-5 1.9-5 5v3H6v4h3v8h4v-8h3.5l.5-4H13V9c0-.7.3-1 1-1Z"/></svg>
        </a>
        <a href="https://www.tiktok.com/" target="_blank" rel="noreferrer" aria-label="TikTok" title="TikTok">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M16.5 2h-3.2v13.2a2.8 2.8 0 1 1-2.8-2.8c.3 0 .6 0 .9.1V9.1a6.5 6.5 0 1 0 5.1 6.3V8.8c1.3.9 2.8 1.4 4.5 1.4V7a4.5 4.5 0 0 1-4.5-5Z"/></svg>
        </a>
        <a class="utility-phone" href="tel:+254700000000" aria-label="Call +254 700 000 000" title="Call +254 700 000 000">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 2.5 3.8 5.3c-.7.7-.9 1.7-.5 2.6 2.5 6.1 6.7 10.3 12.8 12.8.9.4 1.9.2 2.6-.5l2.8-2.8-4.1-4.1-2.2 2.2c-2.1-1.1-3.9-2.9-5-5l2.2-2.2-3.8-3.8Z"/></svg>
        </a>
      </div>
    </div>
  `;
  navigation.parentElement?.insertBefore(utilityBar, navigation);

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
