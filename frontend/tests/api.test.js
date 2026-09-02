import { beforeEach, describe, expect, it, vi } from 'vitest';
import {
  createProject,
  getProjects,
  getStories,
  submitContact,
} from '../src/scripts/api.js';

function jsonResponse(data, status = 200) {
  return {
    status,
    ok: status >= 200 && status < 300,
    headers: { get: () => 'application/json' },
    json: async () => data,
  };
}

describe('API client', () => {
  beforeEach(() => {
    localStorage.clear();
    globalThis.fetch = vi.fn();
  });

  it('fetches projects through the frontend API route', async () => {
    const projects = [{ id: 1, name: 'Learning' }];
    fetch.mockResolvedValue(jsonResponse(projects));

    await expect(getProjects()).resolves.toEqual(projects);
    expect(fetch).toHaveBeenCalledWith('/api/projects', {
      headers: { 'Content-Type': 'application/json' },
    });
  });

  it('fetches stories and sends authenticated headers', async () => {
    localStorage.setItem('token', 'test-token');
    fetch.mockResolvedValue(jsonResponse([]));

    await getStories();

    expect(fetch).toHaveBeenCalledWith('/api/stories', {
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Bearer test-token',
      },
    });
  });

  it('sends project and contact payloads to the backend', async () => {
    fetch.mockResolvedValue(jsonResponse({ id: 2 }));

    await createProject('Learning', 'Education', 'Summary', 'A long enough description.');
    expect(fetch).toHaveBeenNthCalledWith(1, '/api/projects', {
      method: 'POST',
      body: JSON.stringify({
        name: 'Learning',
        category: 'Education',
        summary: 'Summary',
        description: 'A long enough description.',
      }),
      headers: { 'Content-Type': 'application/json' },
    });

    await submitContact('Amina', 'amina@example.com', 'A message that is long enough.');
    expect(fetch).toHaveBeenNthCalledWith(2, '/api/contact', {
      method: 'POST',
      body: JSON.stringify({
        name: 'Amina',
        email: 'amina@example.com',
        message: 'A message that is long enough.',
      }),
      headers: { 'Content-Type': 'application/json' },
    });
  });

  it('throws the backend error detail', async () => {
    fetch.mockResolvedValue(jsonResponse({ detail: 'Invalid data' }, 422));

    await expect(getProjects()).rejects.toThrow('Invalid data');
  });
});