import { getProjects } from './api.js';

const projectGrid = document.querySelector('[data-projects]');

function renderProjects(projects) {
  if (!projects.length) {
    projectGrid.innerHTML = '<p>No projects are available yet.</p>';
    return;
  }

  projectGrid.innerHTML = projects.map((project) => `
    <article class="project-card">
      <p class="eyebrow">${project.category}</p>
      <h3>${project.name}</h3>
      <p class="project-summary">${project.summary}</p>
      <p>${project.description}</p>
    </article>
  `).join('');
}

async function loadProjects() {
  try {
    renderProjects(await getProjects());
  } catch (error) {
    projectGrid.innerHTML = '<p role="alert">Projects could not be loaded. Please try again later.</p>';
  }
}

loadProjects();