import { getStories } from './api.js';

const storyList = document.querySelector('[data-stories]');

function renderStories(stories) {
  if (!stories.length) {
    storyList.innerHTML = '<p>No stories are available yet.</p>';
    return;
  }

  storyList.innerHTML = stories.map((story) => `
    <article class="story-card">
      <div>
        <p class="eyebrow">${story.category} · ${story.year}</p>
        <h2>${story.title}</h2>
      </div>
      <p>${story.excerpt}</p>
    </article>
  `).join('');
}

async function loadStories() {
  try {
    renderStories(await getStories());
  } catch (error) {
    storyList.innerHTML = '<p role="alert">Stories could not be loaded. Please try again later.</p>';
  }
}

loadStories();