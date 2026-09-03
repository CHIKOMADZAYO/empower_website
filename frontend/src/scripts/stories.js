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
      <button class="story-toggle" type="button" aria-expanded="false">
        <span>Learn more</span><span aria-hidden="true">&#8594;</span>
      </button>
      <div class="story-details" hidden>
        <p>${story.content || story.description || `${story.excerpt} Empower works alongside local leaders to turn this community-led progress into lasting opportunity.`}</p>
      </div>
    </article>
  `).join('');

  storyList.querySelectorAll('.story-toggle').forEach((toggle) => {
    toggle.addEventListener('click', () => {
      const details = toggle.nextElementSibling;
      const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!isExpanded));
      toggle.querySelector('span').textContent = isExpanded ? 'Learn more' : 'Show less';
      details.hidden = isExpanded;
    });
  });
}

async function loadStories() {
  try {
    renderStories(await getStories());
  } catch (error) {
    storyList.innerHTML = '<p role="alert">Stories could not be loaded. Please try again later.</p>';
  }
}

loadStories();