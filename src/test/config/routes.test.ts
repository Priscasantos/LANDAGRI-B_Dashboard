import { describe, it, expect } from 'vitest';
import { commandIndex, legacyRedirects, resolveLegacyRedirect } from '../../config/routes';

const LEGACY_EN_TITLES = [
  'Temporal Analysis',
  'Comparative Analysis',
  'Detailed Analysis',
  'Agriculture Overview',
  'Crop Calendar',
  'Agriculture Availability',
];

describe('commandIndex (PT navigation dictionary)', () => {
  it('contains no legacy English sub-route titles', () => {
    const titles = commandIndex.map((entry) => entry.title);
    for (const legacy of LEGACY_EN_TITLES) {
      expect(titles).not.toContain(legacy);
    }
  });

  it('exposes the Fase 3 short PT titles with unchanged urls', () => {
    const byUrl = new Map(commandIndex.map((entry) => [entry.url, entry.title]));
    expect(byUrl.get('/overview')).toBe('Visão Geral');
    expect(byUrl.get('/initiative-analysis')).toBe('Iniciativas');
    expect(byUrl.get('/initiative-analysis/temporal')).toBe('Evolução');
    expect(byUrl.get('/initiative-analysis/comparative')).toBe('Comparar');
    expect(byUrl.get('/initiative-analysis/detailed')).toBe('Ficha');
    expect(byUrl.get('/agricultural-analysis')).toBe('Agricultura');
    expect(byUrl.get('/agricultural-analysis/overview')).toBe('Panorama');
    expect(byUrl.get('/agricultural-analysis/crop-calendar')).toBe('Calendário');
    expect(byUrl.get('/agricultural-analysis/availability')).toBe('Disponibilidade');
    expect(byUrl.get('/predictive')).toBe('Simulador');
    expect(byUrl.get('/about')).toBe('Sobre');
  });

  it('keeps every deep-link url covered by the index (Ctrl+K contract)', () => {
    const urls = commandIndex.map((entry) => entry.url);
    for (const url of [
      '/overview',
      '/initiative-analysis',
      '/initiative-analysis/temporal',
      '/initiative-analysis/comparative',
      '/initiative-analysis/detailed',
      '/agricultural-analysis',
      '/agricultural-analysis/overview',
      '/agricultural-analysis/crop-calendar',
      '/agricultural-analysis/availability',
      '/predictive',
      '/about',
    ]) {
      expect(urls).toContain(url);
    }
  });

  it('carries non-empty PT+EN synonym keywords on every entry', () => {
    for (const entry of commandIndex) {
      expect(entry.keywords.trim().length).toBeGreaterThan(0);
    }
    const byUrl = new Map(commandIndex.map((entry) => [entry.url, entry.keywords]));
    // Spot-check: long-form recall survives the short labels.
    expect(byUrl.get('/initiative-analysis/temporal')).toMatch(/temporal/);
    expect(byUrl.get('/initiative-analysis/comparative')).toMatch(/compar/);
    expect(byUrl.get('/agricultural-analysis/crop-calendar')).toMatch(/calendar/);
    expect(byUrl.get('/predictive')).toMatch(/simulator/);
  });
});

describe('legacyRedirects (alias, não 404)', () => {
  it('resolves known aliases to their canonical targets', () => {
    expect(resolveLegacyRedirect('/home')).toBe('/overview');
    expect(resolveLegacyRedirect('/initiatives')).toBe('/initiative-analysis');
    expect(resolveLegacyRedirect('/agriculture')).toBe('/agricultural-analysis');
    expect(resolveLegacyRedirect('/simulator')).toBe('/predictive');
  });

  it('returns null for canonical routes and unknown paths', () => {
    expect(resolveLegacyRedirect('/overview')).toBeNull();
    expect(resolveLegacyRedirect('/predictive')).toBeNull();
    expect(resolveLegacyRedirect('/definitely-not-a-page')).toBeNull();
    expect(resolveLegacyRedirect('/')).toBeNull();
  });

  it('points every alias at a real route (no alias-to-404)', () => {
    const canonical = new Set([
      '/',
      '/overview',
      '/initiative-analysis',
      '/initiative-analysis/temporal',
      '/initiative-analysis/comparative',
      '/initiative-analysis/detailed',
      '/agricultural-analysis',
      '/agricultural-analysis/overview',
      '/agricultural-analysis/crop-calendar',
      '/agricultural-analysis/availability',
      '/predictive',
      '/about',
    ]);
    for (const alias of legacyRedirects) {
      expect(canonical.has(alias.to)).toBe(true);
    }
  });
});
