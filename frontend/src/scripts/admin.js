import {
  createProject,
  createStory,
  deleteContactMessage,
  deleteProject,
  deleteStory,
  getContactMessages,
  getProfile,
  getProjects,
  getStories,
} from './api.js';
import { clearToken, decodeToken, getToken } from './auth.js';

const dashboard = document.querySelector('[data-admin-dashboard]');
const status = document.querySelector('[data-admin-status]');

function setStatus(message, isError = false) {
  status.textContent = message;
  status.dataset.state = isError ? 'error' : 'success';
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;',
  })[character]);
}

function renderList(selector, items, emptyMessage, renderItem) {
  const element = document.querySelector(selector);
  element.innerHTML = items.length ? items.map(renderItem).join('') : `<p class="admin-empty">${emptyMessage}</p>`;
}

function renderOverview(projects, stories, contacts) {
  document.querySelector('[data-count="projects"]').textContent = projects.length;
  document.querySelector('[data-count="stories"]').textContent = stories.length;
  document.querySelector('[data-count="contacts"]').textContent = contacts.length;
}

function renderProjects(projects) {
  renderList('[data-project-list]', projects, 'No projects yet.', (project) => `
    <article class="admin-row">
      <div><strong>${escapeHtml(project.name)}</strong><span>${escapeHtml(project.category)}</span><p>${escapeHtml(project.summary)}</p></div>
      <button class="admin-delete" type="button" data-delete-project="${project.id}">Delete</button>
    </article>`);
}

function renderStories(stories) {
  renderList('[data-story-list]', stories, 'No stories yet.', (story) => `
    <article class="admin-row">
      <div><strong>${escapeHtml(story.title)}</strong><span>${escapeHtml(story.category)} / ${escapeHtml(story.year)}</span><p>${escapeHtml(story.excerpt)}</p></div>
      <button class="admin-delete" type="button" data-delete-story="${story.id}">Delete</button>
    </article>`);
}

function renderContacts(contacts) {
  renderList('[data-contact-list]', contacts, 'No contact messages yet.', (contact) => `
    <article class="admin-row">
      <div><strong>${escapeHtml(contact.name)}</strong><span>${escapeHtml(contact.email)}</span><p>${escapeHtml(contact.message)}</p></div>
      <button class="admin-delete" type="button" data-delete-contact="${contact.id}">Delete</button>
    </article>`);
}

async function loadDashboard() {
  setStatus('Loading dashboard...');
  try {
    const [projects, stories, contacts] = await Promise.all([
      getProjects(), getStories(), getContactMessages(),
    ]);
    renderOverview(projects, stories, contacts);
    renderProjects(projects);
    renderStories(stories);
    renderContacts(contacts);
    setStatus('Dashboard updated.');
  } catch (error) {
    setStatus(error.message || 'Unable to load dashboard data.', true);
  }
}

async function handleCreate(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const fields = Object.fromEntries(new FormData(form));
  try {
    if (form.matches('[data-project-form]')) {
      await createProject(fields.name, fields.category, fields.summary, fields.description);
    } else {
      await createStory(fields.title, fields.category, fields.excerpt, Number(fields.year));
    }
    form.reset();
    setStatus('Published successfully.');
    await loadDashboard();
  } catch (error) {
    setStatus(error.message || 'Unable to publish item.', true);
  }
}

document.addEventListener('click', async (event) => {
  const button = event.target.closest('[data-delete-project], [data-delete-story], [data-delete-contact]');
  if (!button || !window.confirm('Delete this item?')) return;
  try {
    if (button.dataset.deleteProject) await deleteProject(button.dataset.deleteProject);
    if (button.dataset.deleteStory) await deleteStory(button.dataset.deleteStory);
    if (button.dataset.deleteContact) await deleteContactMessage(button.dataset.deleteContact);
    await loadDashboard();
  } catch (error) {
    setStatus(error.message || 'Unable to delete item.', true);
  }
});

document.querySelectorAll('[data-admin-form]').forEach((form) => form.addEventListener('submit', handleCreate));
document.querySelector('[data-logout]')?.addEventListener('click', () => {
  clearToken();
  window.location.href = '/login.html';
});

async function initialize() {
  const token = getToken();
  const claims = token ? decodeToken(token) : null;
  if (!claims || claims.role !== 'admin') {
    dashboard.innerHTML = '<div class="admin-denied"><h1>Admin access required</h1><p>Sign in with an administrator account to manage Empower.</p><a class="button button-primary" href="login.html">Go to sign in</a></div>';
    return;
  }

  try {
    const profile = await getProfile();
    document.querySelector('[data-admin-user]').textContent = profile?.user?.username || claims.username || 'Administrator';
    await loadDashboard();
  } catch (error) {
    setStatus(error.message || 'Unable to verify administrator access.', true);
  }
}

initialize();