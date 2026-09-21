/**
 * Empower Frontend - Admin dashboard
 * Renders the list of registered users (admin-only endpoint).
 */

import { getUsers } from './api.js';
import { requireAuth } from './auth.js';

/**
 * Build a single user card using textContent to avoid XSS injection.
 */
function createUserElement(user) {
  const userDiv = document.createElement('div');
  userDiv.classList.add('user');

  const fields = [
    { label: 'ID', value: user.id },
    { label: 'Name', value: user.username },
    { label: 'Email', value: user.email },
    { label: 'Role', value: user.role },
  ];

  fields.forEach(({ label, value }) => {
    const paragraph = document.createElement('p');
    const strong = document.createElement('strong');
    strong.textContent = `${label}:`;
    paragraph.append(strong, ` ${value ?? ''}`);
    userDiv.appendChild(paragraph);
  });

  return userDiv;
}

/**
 * Render the user list into the admin panel.
 */
function renderUsers(container, users) {
  container.innerHTML = '';

  if (!users || users.length === 0) {
    const empty = document.createElement('p');
    empty.textContent = 'No users found.';
    container.appendChild(empty);
    return;
  }

  users.forEach((user) => container.appendChild(createUserElement(user)));
}

/**
 * Load users from the API and display them in the admin panel.
 */
export async function displayUserData() {
  const userDataContainer = document.getElementById('user-data');
  if (!userDataContainer) return;

  userDataContainer.textContent = 'Loading users...';

  try {
    const users = await getUsers();
    renderUsers(userDataContainer, users);
  } catch (error) {
    const message = document.createElement('p');
    message.setAttribute('role', 'alert');
    message.textContent = error.message || 'Users could not be loaded. Please try again later.';
    userDataContainer.innerHTML = '';
    userDataContainer.appendChild(message);
  }
}

if (typeof window !== 'undefined') {
  window.addEventListener('DOMContentLoaded', () => {
    requireAuth();
    displayUserData();
  });
}

export default displayUserData;