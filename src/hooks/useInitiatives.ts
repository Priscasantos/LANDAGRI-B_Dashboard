import { useEffect, useState } from 'react';
import { useDashboardStore } from '../stores/dashboardStore';
import { getBasename } from '../config/routes';
import { parseInitiatives } from '../lib/dataParser';
import type { InitiativeMetadata, InitiativeRow } from '../types/initiative';
import type { SensorMap } from '../types/sensor';

/** Runtime data is served under the router basename (gh-pages sub-path). */
export function dataUrl(file: string): string {
  // Strip a trailing slash so the dev basename '/' yields '/data/...'
  // instead of the protocol-relative '//data/...'.
  const base = getBasename().replace(/\/+$/, '');
  return `${base}/data/processed/${file}`;
}


async function fetchJson(file: string): Promise<unknown> {
  const res = await fetch(dataUrl(file));
  if (!res.ok) {
    throw new Error(`Failed to load ${file}: HTTP ${res.status}`);
  }
  return res.json();
}


function isPlainRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}


/**
 * Minimal runtime schema guard for `initiatives.json`.
 * Loud failure (throw) instead of a silent cast — an unexpected shape
 * must surface as a store error, never as an empty dashboard.
 */
export function validateInitiativesPayload(data: unknown): Record<string, InitiativeMetadata> {
  if (!isPlainRecord(data)) {
    throw new Error('Invalid initiatives.json: expected a JSON object keyed by initiative name');
  }
  const entries = Object.entries(data);
  if (entries.length === 0) {
    throw new Error('Invalid initiatives.json: empty payload');
  }
  const valid = entries.filter(
    ([, v]) => isPlainRecord(v) && typeof (v as Record<string, unknown>).acronym === 'string',
  );
  if (valid.length === 0) {
    throw new Error(
      `Invalid initiatives.json: 0 of ${entries.length} entries have the required 'acronym' field`,
    );
  }
  return Object.fromEntries(valid) as unknown as Record<string, InitiativeMetadata>;
}


/** Minimal runtime schema guard for `sensors.json` (same loud-failure rule). */
export function validateSensorsPayload(data: unknown): SensorMap {
  if (!isPlainRecord(data)) {
    throw new Error('Invalid sensors.json: expected a JSON object keyed by sensor key');
  }
  if (Object.keys(data).length === 0) {
    throw new Error('Invalid sensors.json: empty payload');
  }
  return data as unknown as SensorMap;
}

/**
 * Hook to load and parse initiative data on mount using fetch (not import)
 */
export function useInitiatives() {
  const { setInitiatives, setSensorsData, setLoading, setError, initiatives, isLoading, error } = useDashboardStore();
  const [sensors, setSensors] = useState<SensorMap>({});

  useEffect(() => {
    let cancelled = false;
    
    async function loadData() {
      try {
        setLoading(true);
        
        const [initiativesData, sensorsData] = await Promise.all([
          fetchJson('initiatives.json'),
          fetchJson('sensors.json'),
        ]);
        
        if (cancelled) return;
        
        const metadata = validateInitiativesPayload(initiativesData);
        const parsed = parseInitiatives(metadata);
        const sensorsMap = validateSensorsPayload(sensorsData);
        
        if (!cancelled) {
          setInitiatives(parsed, metadata);
          setSensorsData(sensorsMap);
          setSensors(sensorsMap);
        }
      } catch (err) {
        if (!cancelled) {
          const message = err instanceof Error ? err.message : 'Failed to load data';
          setError(message);
        }
      }
    }
    
    loadData();
    
    return () => { cancelled = true; };
  }, [setInitiatives, setSensorsData, setLoading, setError]);

  return { initiatives, sensors, isLoading, error };
}

/**
 * Hook to get initiative data for a specific module
 */
export function useFilteredInitiatives(): InitiativeRow[] {
  return useDashboardStore((state) => state.getFilteredInitiatives());
}

/**
 * Hook to get a single initiative by name
 */
export function useInitiative(name: string | null): InitiativeRow | undefined {
  return useDashboardStore((state) => (name ? state.getInitiativeByName(name) : undefined));
}
