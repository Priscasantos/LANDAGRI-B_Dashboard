import { describe, expect, it, vi, afterEach } from 'vitest';
import {
  DEFAULT_BASENAME,
  REDIRECT_STORAGE_KEY,
  appRoutes,
  commandIndex,
  getBasename,
  getRedirectPath,
} from './routes';

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
      '*',
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

  it('trims whitespace and collapses duplicate slashes', () => {
    expect(getBasename({ VITE_BASENAME: '  /custom-base// ', DEV: false })).toBe(
      '/custom-base',
    );
  });
});

describe('routes config — Fase 1 shell metadata', () => {
  it('exposes a non-empty title + description for every route', () => {
    expect(appRoutes.length).toBeGreaterThan(0);
    for (const route of appRoutes) {
      expect(route.title.length).toBeGreaterThan(0);
      expect(route.description.length).toBeGreaterThan(0);
    }
  });

  it('declares a catch-all 404 route redirecting to /', () => {
    const notFound = appRoutes.find((r) => r.path === '*');
    expect(notFound).toBeDefined();
    expect(notFound?.redirectTo).toBe('/');
  });

  it('every route Component is React.lazy (Suspense fallback applies)', () => {
    const LAZY = Symbol.for('react.lazy');
    for (const route of appRoutes) {
      expect(
        (route.Component as unknown as { $$typeof: symbol }).$$typeof,
      ).toBe(LAZY);
    }
  });

  it('command index covers the 5 modules + initiative/agricultural sub-routes', () => {
    const urls = commandIndex.map((entry) => entry.url);
    for (const url of [
      '/overview',
      '/initiative-analysis',
      '/agricultural-analysis',
      '/predictive',
      '/about',
    ]) {
      expect(urls).toContain(url);
    }
    for (const url of [
      '/initiative-analysis/temporal',
      '/initiative-analysis/comparative',
      '/initiative-analysis/detailed',
      '/agricultural-analysis/overview',
      '/agricultural-analysis/crop-calendar',
      '/agricultural-analysis/availability',
    ]) {
      expect(urls).toContain(url);
    }
  });
});

describe('getRedirectPath (gh-pages 404 restore)', () => {
  function makeStorage(initial?: Record<string, string>) {
    const store = new Map<string, string>(Object.entries(initial ?? {}));
    return {
      getItem: (key: string): string | null => store.get(key) ?? null,
      removeItem: (key: string): void => {
        store.delete(key);
      },
      has: (key: string): boolean => store.has(key),
    };
  }

  it('returns null when nothing was stored', () => {
    expect(getRedirectPath(makeStorage())).toBeNull();
  });

  it('consumes and returns a valid deep link exactly once', () => {
    const storage = makeStorage({
      [REDIRECT_STORAGE_KEY]: '/predictive',
    });
    expect(getRedirectPath(storage)).toBe('/predictive');
    expect(storage.has(REDIRECT_STORAGE_KEY)).toBe(false);
  });

  it('ignores root-only and non-path values', () => {
    expect(
      getRedirectPath(makeStorage({ [REDIRECT_STORAGE_KEY]: '/' })),
    ).toBeNull();
    expect(
      getRedirectPath(
        makeStorage({ [REDIRECT_STORAGE_KEY]: 'https://evil.test/x' }),
      ),
    ).toBeNull();
  });
});
