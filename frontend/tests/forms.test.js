import { describe, expect, it, vi } from 'vitest';
import { handleContactSubmit } from '../src/scripts/contact.js';

describe('contact form', () => {
  it('validates required fields before making a request', async () => {
    document.body.innerHTML = `
      <form data-contact-form>
        <input name="name" value="" />
        <input name="email" value="" />
        <textarea name="message"></textarea>
      </form>
      <p data-contact-status></p>
    `;
    const form = document.querySelector('[data-contact-form]');
    const fetchSpy = vi.spyOn(globalThis, 'fetch');

    await handleContactSubmit({ preventDefault: vi.fn(), currentTarget: form });

    expect(document.querySelector('[data-contact-status]').textContent).toBe('Please complete all fields.');
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it('submits valid contact details and resets the form', async () => {
    document.body.innerHTML = `
      <form data-contact-form>
        <input name="name" />
        <input name="email" />
        <textarea name="message"></textarea>
      </form>
      <p data-contact-status></p>
    `;
    document.querySelector('[name="name"]').value = 'Amina Yusuf';
    document.querySelector('[name="email"]').value = 'amina@example.com';
    document.querySelector('[name="message"]').value = 'A valid message that is long enough.';
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 201,
      headers: { get: () => 'application/json' },
      json: async () => ({ message: 'received' }),
    });

    await handleContactSubmit({ preventDefault: vi.fn(), currentTarget: document.querySelector('form') });

    expect(fetch).toHaveBeenCalledWith('/api/contact', expect.objectContaining({ method: 'POST' }));
    expect(document.querySelector('[data-contact-form]').querySelector('[name="name"]').value).toBe('');
    expect(document.querySelector('[data-contact-status]').textContent).toBe('Thanks. Your message has been sent.');
  });
});