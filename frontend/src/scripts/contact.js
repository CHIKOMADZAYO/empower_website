import { submitContact } from './api.js';

const contactForm = document.querySelector('[data-contact-form]');
const contactStatus = document.querySelector('[data-contact-status]');

function setStatus(message, isError = false) {
  const status = document.querySelector('[data-contact-status]');
  if (!status) return;

  status.textContent = message;
  status.style.color = isError ? '#b42318' : '#0f766e';
}

export async function handleContactSubmit(event) {
  event.preventDefault();

  const form = event.currentTarget;
  const formData = new FormData(form);
  const name = formData.get('name')?.trim();
  const email = formData.get('email')?.trim();
  const message = formData.get('message')?.trim();

  if (!name || !email || !message) {
    setStatus('Please complete all fields.', true);
    return;
  }

  try {
    setStatus('Sending your message...');
    await submitContact(name, email, message);
    form.reset();
    setStatus('Thanks. Your message has been sent.');
  } catch (error) {
    setStatus(error.message || 'Unable to send your message. Please try again.', true);
  }
}

if (contactForm && contactStatus) {
  contactForm.addEventListener('submit', handleContactSubmit);
}