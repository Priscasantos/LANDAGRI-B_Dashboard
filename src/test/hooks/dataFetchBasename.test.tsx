import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useDashboardStore } from '../../stores/dashboardStore';
import { dataUrl, useInitiatives } from '../../hooks/useInitiatives';

const initiativesFixture = {
  BaseInitiative: { acronym: 'BAS', coverage: 'national', available_years: [2020] },
};
const sensorsFixture = { s2: { name: 'Sentinel-2' } };

describe('runtime data fetch via VITE_BASENAME (Fase 2 integration)', () => {
  beforeEach(() => {
    useDashboardStore.setState({ initiatives: [], rawMetadata: {}, sensors: {}, isLoading: false, error: null });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
  });

  it('dataUrl prefixes runtime files with the configured basename', () => {
    vi.stubEnv('VITE_BASENAME', '/LANDAGRI-B_Dashboard');
    expect(dataUrl('initiatives.json')).toBe('/LANDAGRI-B_Dashboard/data/processed/initiatives.json');
    expect(dataUrl('sensors.json')).toBe('/LANDAGRI-B_Dashboard/data/processed/sensors.json');
  });

  it('fetches both runtime files under the basename and populates the store', async () => {
    vi.stubEnv('VITE_BASENAME', '/LANDAGRI-B_Dashboard');
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(initiativesFixture) } as Response)
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(sensorsFixture) } as Response);
    vi.stubGlobal('fetch', fetchMock);

    const { result } = renderHook(() => useInitiatives());
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(fetchMock.mock.calls[0][0]).toBe('/LANDAGRI-B_Dashboard/data/processed/initiatives.json');
    expect(fetchMock.mock.calls[1][0]).toBe('/LANDAGRI-B_Dashboard/data/processed/sensors.json');
    expect(result.current.initiatives).toHaveLength(1);
    expect(result.current.error).toBeNull();
  });
});
