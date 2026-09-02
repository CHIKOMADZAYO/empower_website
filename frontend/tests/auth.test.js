import { beforeEach, describe, expect, it } from 'vitest';
import {
  clearToken,
  decodeToken,
  getToken,
  isAuthenticated,
  setToken,
} from '../src/scripts/auth.js';

describe('authentication helpers', () => {
  beforeEach(() => localStorage.clear());

  it('stores, reads, and clears the access token', () => {
    setToken('token-value');
    expect(getToken()).toBe('token-value');
    expect(isAuthenticated()).toBe(true);

    clearToken();
    expect(getToken()).toBeNull();
    expect(isAuthenticated()).toBe(false);
  });

  it('decodes valid JWT payloads and rejects malformed tokens', () => {
    const payload = btoa(JSON.stringify({ sub: '1', role: 'viewer' }))
      .replace(/=/g, '')
      .replace(/\+/g, '-')
      .replace(/\//g, '_');
    expect(decodeToken(`header.${payload}.signature`)).toEqual({ sub: '1', role: 'viewer' });
    expect(decodeToken('invalid')).toBeNull();
  });
});