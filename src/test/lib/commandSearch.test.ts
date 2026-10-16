import { describe, it, expect } from 'vitest';
import {
  filterCommandEntries,
  loadRecents,
  normalizeSearchText,
  orderWithRecents,
  recordRecent,
  type PaletteEntry,
} from '../../lib/commandSearch';

const ENTRIES: PaletteEntry[] = [
  {
    url: '/initiative-analysis/temporal',
    title: 'Evolução',
    group: 'Território',
    ptTitle: 'Evolução',
    enTitle: 'Evolution',
    enGroup: 'Territory',
    keywords: 'temporal evolucao evolution serie historico',
  },
  {
    url: '/predictive',
    title: 'Simulador',
    group: 'Mais',
    ptTitle: 'Simulador',
    enTitle: 'Simulator',
    enGroup: 'More',
    keywords: 'simulador simulator preditivo predictive',
  },
];

function memStorage(initial: Record<string, string> = {}): {
  getItem: (k: string) => string | null;
  setItem: (k: string, v: string) => void;
} {
  const store = new Map(Object.entries(initial));
  return {
    getItem: (k) => store.get(k) ?? null,
    setItem: (k, v) => {
      store.set(k, v);
    },
  };
}

describe('normalizeSearchText', () => {
  it('matches with or without accents', () => {
    expect(normalizeSearchText('Evolução')).toBe('evolucao');
    expect(normalizeSearchText('  Calendário ')).toBe('calendario');
  });
});

describe('filterCommandEntries (sinônimos PT+EN+url)', () => {
  it('finds by PT synonym regardless of active locale title', () => {
    expect(filterCommandEntries(ENTRIES, 'temporal').map((e) => e.url)).toContain(
      '/initiative-analysis/temporal',
    );
  });

  it('finds by EN synonym while UI is PT', () => {
    expect(filterCommandEntries(ENTRIES, 'evolution').map((e) => e.url)).toContain(
      '/initiative-analysis/temporal',
    );
    expect(filterCommandEntries(ENTRIES, 'simulator').map((e) => e.url)).toContain('/predictive');
  });

  it('finds by url fragment', () => {
    expect(filterCommandEntries(ENTRIES, 'predictive').map((e) => e.url)).toContain('/predictive');
  });

  it('requires every term (AND) and ignores accents/case', () => {
    expect(filterCommandEntries(ENTRIES, 'EVOLUCAO temporal')).toHaveLength(1);
    expect(filterCommandEntries(ENTRIES, 'evolucao simulador')).toHaveLength(0);
  });

  it('returns everything on empty query', () => {
    expect(filterCommandEntries(ENTRIES, '   ')).toHaveLength(2);
  });
});

describe('recents', () => {
  it('records most-recent-first with dedupe and cap', () => {
    const storage = memStorage();
    recordRecent(storage, '/a');
    recordRecent(storage, '/b');
    recordRecent(storage, '/a');
    expect(loadRecents(storage)).toEqual(['/a', '/b']);
    for (const url of ['/c', '/d', '/e', '/f']) recordRecent(storage, url);
    const recents = loadRecents(storage);
    expect(recents).toHaveLength(5);
    expect(recents[0]).toBe('/f');
  });

  it('tolerates broken JSON', () => {
    expect(loadRecents(memStorage({ 'landagri-recent-pages': '%%%' }))).toEqual([]);
  });

  it('orders known entries recents-first, stable otherwise', () => {
    const ordered = orderWithRecents(ENTRIES, ['/predictive']);
    expect(ordered.map((e) => e.url)).toEqual(['/predictive', '/initiative-analysis/temporal']);
  });
});
