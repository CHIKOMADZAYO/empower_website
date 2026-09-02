import { afterEach, describe, expect, it, vi } from 'vitest';

const projectData = [
  {
    category: 'Education',
    name: 'Learning',
    summary: 'Open doors to opportunity.',
    description: 'Learning spaces and practical skills for young people.',
  },
];

const storyData = [
  {
    category: 'Learning',
    year: 2025,
    title: 'The library became our meeting place.',
    excerpt: 'A community reading room became a place for young people.',
  },
];

async function loadPage(selector, modulePath, data) {
  const attribute = selector.includes('stories') ? 'data-stories' : 'data-projects';
  document.body.innerHTML = `<div ${attribute}></div>`;
  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    status: 200,
    headers: { get: () => 'application/json' },
    json: async () => data,
  });
  vi.resetModules();
  if (modulePath.includes('stories')) {
    await import('../src/scripts/stories.js');
  } else {
    await import('../src/scripts/projects.js');
  }
  await vi.waitFor(() => expect(document.querySelector(selector).querySelector('article')).not.toBeNull());
}

afterEach(() => {
  document.body.innerHTML = '';
  vi.restoreAllMocks();
});

describe('data pages', () => {
  it('renders projects returned by the backend', async () => {
    await loadPage('[data-projects]', '../src/scripts/projects.js', projectData);

    expect(document.querySelector('[data-projects] h3').textContent).toBe('Learning');
    expect(document.querySelector('[data-projects]').textContent).toContain('Education');
    expect(fetch).toHaveBeenCalledWith('/api/projects', {
      headers: { 'Content-Type': 'application/json' },
    });
  });

  it('renders stories returned by the backend', async () => {
    await loadPage('[data-stories]', '../src/scripts/stories.js', storyData);

    expect(document.querySelector('[data-stories] h2').textContent).toContain('library');
    expect(document.querySelector('[data-stories]').textContent).toContain('2025');
  });

  it('shows a useful error when a collection cannot load', async () => {
    document.body.innerHTML = '<div data-projects></div>';
    globalThis.fetch = vi.fn().mockRejectedValue(new Error('offline'));
    vi.resetModules();
    await import('../src/scripts/projects.js');

    await vi.waitFor(() => expect(document.querySelector('[role="alert"]')).not.toBeNull());
    expect(document.querySelector('[role="alert"]').textContent).toContain('could not be loaded');
  });
});