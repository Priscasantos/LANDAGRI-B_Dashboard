import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { useDashboardStore } from '../../stores/dashboardStore';
import { dataUrl, useInitiatives, validateInitiativesPayload, validateSensorsPayload } from '../../hooks/useInitiatives';

const initiativesFixture = {
  TestInitiative: {
    acronym: 'TST',
    provider: 'Test Provider',
    coverage: 'national',
    methodology: 'Shallow ML',
    available_years: [2020],
  },
};
const sensorsFixture = { landsat: { name: 'Landsat' } };

function wrapperWithClient() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false } },
  });
  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
  return Wrapper;
}

describe('useInitiatives (Fase 3)', () => {
  beforeEach(() => {
    useDashboardStore.setState({
      initiatives: [],
      rawMetadata: {},
      sensors: {},
      isLoading: false,
      error: null,
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('loads initiatives + sensors and populates the zustand store', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(initiativesFixture) } as Response)
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(sensorsFixture) } as Response);
    vi.stubGlobal('fetch', fetchMock);

    const { result } = renderHook(() => useInitiatives(), { wrapper: wrapperWithClient() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(fetchMock.mock.calls[0][0]).toBe(dataUrl('initiatives.json'));
    expect(fetchMock.mock.calls[1][0]).toBe(dataUrl('sensors.json'));
    expect(result.current.initiatives).toHaveLength(1);
    expect(result.current.initiatives[0].Name).toBe('TestInitiative');
    expect(result.current.sensors).toEqual(sensorsFixture);
    expect(result.current.error).toBeNull();
  });

  it('surfaces HTTP errors via store error (no throw)', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.resolve({ ok: false, status: 404, json: () => Promise.resolve({}) } as unknown as Response)),
    );

    const { result } = renderHook(() => useInitiatives(), { wrapper: wrapperWithClient() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.error).toContain('404');
    expect(result.current.initiatives).toEqual([]);
  });

  it('surfaces fetch rejection via store error', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.reject(new Error('network down'))),
    );

    const { result } = renderHook(() => useInitiatives(), { wrapper: wrapperWithClient() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.error).toBe('network down');
  });

  it('cancellation on unmount: pending fetch never writes to the store', async () => {
    let resolveFetch!: (value: unknown) => void;
    const gate = new Promise((resolve) => {
      resolveFetch = resolve;
    });
    vi.stubGlobal(
      'fetch',
      vi.fn(() =>
        gate.then(() => ({ ok: true, json: () => Promise.resolve(initiativesFixture) }) as unknown as Response),
      ),
    );

    const { unmount } = renderHook(() => useInitiatives(), { wrapper: wrapperWithClient() });
    expect(useDashboardStore.getState().isLoading).toBe(true);

    unmount(); // cancel before fetch settles
    await act(async () => {
      resolveFetch(undefined);
      await gate;
    });

    // Cancelled guard: store untouched by the late response.
    expect(useDashboardStore.getState().initiatives).toEqual([]);
    expect(useDashboardStore.getState().error).toBeNull();
  });

  it('dataUrl never yields a protocol-relative // URL (dev basename is /)', () => {
    for (const f of ['initiatives.json', 'sensors.json']) {
      const url = dataUrl(f);
      expect(url.startsWith('//')).toBe(false);
      expect(url.endsWith(`/data/processed/${f}`)).toBe(true);
    }
  });

  it('rejects a malformed initiatives payload via store error (no silent [])', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(['not', 'an', 'object']) } as unknown as Response)
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(sensorsFixture) } as unknown as Response);
    vi.stubGlobal('fetch', fetchMock);

    const { result } = renderHook(() => useInitiatives(), { wrapper: wrapperWithClient() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.error).toContain('Invalid initiatives.json');
    expect(result.current.initiatives).toEqual([]);
  });

  it('rejects entries without acronym instead of casting silently', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ Ghost: { provider: 'x' } }) } as unknown as Response)
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(sensorsFixture) } as unknown as Response);
    vi.stubGlobal('fetch', fetchMock);

    const { result } = renderHook(() => useInitiatives(), { wrapper: wrapperWithClient() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.error).toContain("required 'acronym' field");
  });

  it('validateSensorsPayload rejects non-object and empty payloads', () => {
    expect(() => validateSensorsPayload(null)).toThrow('Invalid sensors.json');
    expect(() => validateSensorsPayload([])).toThrow('Invalid sensors.json');
    expect(() => validateSensorsPayload({})).toThrow('empty payload');
    expect(validateSensorsPayload(sensorsFixture)).toEqual(sensorsFixture);
  });

  it('validateInitiativesPayload rejects non-object and empty payloads', () => {
    expect(() => validateInitiativesPayload(null)).toThrow('Invalid initiatives.json');
    expect(() => validateInitiativesPayload({})).toThrow('empty payload');
  });
});
