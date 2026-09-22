/**
 * Empower Frontend - Main Entry Point
 */

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
  const brand = navigation?.querySelector('.brand');
  if (!navigation || !menu) return;

  let toggle = navigation.querySelector('.nav-toggle');
  if (!toggle) {
    toggle = document.createElement('button');
    toggle.className = 'nav-toggle';
    toggle.type = 'button';
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-controls', 'primary-navigation');
    toggle.setAttribute('aria-label', 'Open navigation menu');
    toggle.innerHTML = '<span></span><span></span><span></span>';
    menu.id = 'primary-navigation';
    if (brand && brand.nextSibling) navigation.insertBefore(toggle, brand.nextSibling);
    else navigation.insertBefore(toggle, menu);
  }

  toggle.addEventListener('click', () => {
    const isOpen = navigation.classList.toggle('nav-open');
    toggle.setAttribute('aria-expanded', String(isOpen));
    toggle.setAttribute('aria-label', isOpen ? 'Close navigation menu' : 'Open navigation menu');
  });

  menu.addEventListener('click', (e) => {
    if (e.target.closest('a')) navigation.classList.remove('nav-open');
  });
}

function setupReveal() {
  const els = document.querySelectorAll('.reveal');
  if (!els.length) return;
  if (!('IntersectionObserver' in window)) {
    els.forEach((el) => el.classList.add('visible'));
    return;
  }
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  els.forEach((el) => io.observe(el));
}

function setupAmounts() {
  document.querySelectorAll('.amount-grid').forEach((grid) => {
    grid.addEventListener('click', (e) => {
      const btn = e.target.closest('.amount');
      if (!btn) return;
      grid.querySelectorAll('.amount').forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
  setupNavigation();
  setupNewsletter();
  setupReveal();
  setupAmounts();
});

function setupNewsletter() {
  const form = document.querySelector('[data-newsletter-form]');
  if (!form || !window.API) return;
  const status = form.querySelector('[data-newsletter-status]');
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const email = new FormData(form).get('email');
    if (status) status.textContent = 'Subscribing…';
    try {
      await window.API.submitContact('Newsletter subscriber', String(email), 'Please subscribe me to quarterly field notes.');
      if (status) {
        status.textContent = 'Thank you! Please watch your inbox to confirm.';
        status.dataset.state = 'connected';
      }
      form.reset();
    } catch (error) {
      if (status) {
        status.textContent = 'Something went wrong. Please email hello@empower.org to subscribe.';
        status.dataset.state = 'offline';
      }
    }
  });
}
