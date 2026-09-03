import { afterEach, describe, expect, it, vi } from 'vitest';

afterEach(() => {
  document.body.innerHTML = '';
  localStorage.clear();
  vi.restoreAllMocks();
  vi.resetModules();
});

describe('admin dashboard bootstrap', () => {
  it('does not crash when the admin DOM is not present', async () => {
    document.body.innerHTML = '<main><p>regular page</p></main>';

    await expect(import('../src/scripts/admin.js')).resolves.toBeDefined();
  });
});
