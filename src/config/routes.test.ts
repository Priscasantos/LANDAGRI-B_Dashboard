import { describe, expect, it, vi, afterEach } from 'vitest';
import { DEFAULT_BASENAME, appRoutes, getBasename } from './routes';

describe('routes config (Fase 1 shell)', () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it('preserves the 5 existing route patterns', () => {
    const paths = appRoutes.map((r) => r.path);
    expect(paths).toEqual([
      '/',
      '/overview',
      '/initiative-analysis/*',
      '/agricultural-analysis/*',
      '/predictive',
      '/about',
    ]);
  });

  it('defaults basename to the gh-pages path in prod', () => {
    expect(DEFAULT_BASENAME).toBe('/LANDAGRI-B_Dashboard');
    expect(getBasename({ VITE_BASENAME: '', DEV: false })).toBe(
      '/LANDAGRI-B_Dashboard',
    );
  });

  it('uses / in dev so vite dev at localhost works without a sub-path', () => {
    expect(getBasename({ VITE_BASENAME: '', DEV: true })).toBe('/');
  });

  it('honours VITE_BASENAME when set (normalised, no trailing slash)', () => {
    expect(getBasename({ VITE_BASENAME: '/custom-base', DEV: false })).toBe(
      '/custom-base',
    );
    expect(getBasename({ VITE_BASENAME: '/custom-base/', DEV: true })).toBe(
      '/custom-base',
    );
    // Explicit env wins even in dev (mirrors vite.config.ts).
    expect(getBasename({ VITE_BASENAME: 'custom', DEV: true })).toBe(
      '/custom',
    );
  });

  it('live env: explicit VITE_BASENAME is honoured', () => {
    vi.stubEnv('VITE_BASENAME', '/custom-base');
    expect(getBasename()).toBe('/custom-base');
  });
});
