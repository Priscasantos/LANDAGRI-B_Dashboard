/**
 * Fase 3 IA enxuta: helpers puros da paleta de comando (testáveis sem DOM).
 * Busca casa PT + EN + url + sinônimos, insensível a acentos e caixa.
 */

export interface PaletteEntry {
  url: string;
  /** Título no locale ativo. */
  title: string;
  /** Grupo no locale ativo. */
  group: string;
  /** Título PT canônico (fallback/índice). */
  ptTitle: string;
  /** Título EN (sinônimo cross-locale). */
  enTitle: string;
  /** Grupo EN (sinônimo cross-locale). */
  enGroup: string;
  /** Sinônimos espaço-separados vindos de `commandIndex`. */
  keywords: string;
  /** Urls recentes primeiro (ordenação), nunca filtro. */
  recent?: boolean;
}

const RECENT_KEY = 'landagri-recent-pages';
const MAX_RECENT = 5;

/** Minúsculas + sem diacríticos para casar "evolucao" ↔ "Evolução". */
export function normalizeSearchText(raw: string): string {
  return raw
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .trim();
}

function entryHaystack(entry: PaletteEntry): string {
  return normalizeSearchText(
    [entry.title, entry.group, entry.ptTitle, entry.enTitle, entry.enGroup, entry.url, entry.keywords].join(' '),
  );
}

/**
 * Filtra por AND de termos (todos os termos precisam aparecer em algum
 * campo). Query vazia retorna tudo (chamador ordena recentes primeiro).
 */
export function filterCommandEntries(entries: PaletteEntry[], query: string): PaletteEntry[] {
  const terms = normalizeSearchText(query).split(/\s+/).filter(Boolean);
  if (terms.length === 0) return entries;
  return entries.filter((entry) => {
    const haystack = entryHaystack(entry);
    return terms.every((term) => haystack.includes(term));
  });
}

/** Recentes primeiro, estáveis; entradas fora dos recentes mantêm a ordem. */
export function orderWithRecents(entries: PaletteEntry[], recentUrls: string[]): PaletteEntry[] {
  if (recentUrls.length === 0) return entries;
  const rank = new Map(recentUrls.map((url, index) => [url, index]));
  return [...entries].sort((a, b) => {
    const ra = rank.has(a.url) ? (rank.get(a.url) as number) : Number.MAX_SAFE_INTEGER;
    const rb = rank.has(b.url) ? (rank.get(b.url) as number) : Number.MAX_SAFE_INTEGER;
    return ra - rb;
  });
}

export interface RecentStorage {
  getItem: (key: string) => string | null;
  setItem: (key: string, value: string) => void;
}

/** Lê os recentes (tolerante a JSON quebrado — retorna []). */
export function loadRecents(storage: RecentStorage): string[] {
  try {
    const raw = storage.getItem(RECENT_KEY);
    if (!raw) return [];
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter((item): item is string => typeof item === 'string').slice(0, MAX_RECENT);
  } catch {
    return [];
  }
}

/** Registra a visita (dedupe + most-recent-first, teto MAX_RECENT). */
export function recordRecent(storage: RecentStorage, url: string): string[] {
  const next = [url, ...loadRecents(storage).filter((item) => item !== url)].slice(0, MAX_RECENT);
  try {
    storage.setItem(RECENT_KEY, JSON.stringify(next));
  } catch {
    /* private mode: recentes viram sessão-volátil */
  }
  return next;
}
