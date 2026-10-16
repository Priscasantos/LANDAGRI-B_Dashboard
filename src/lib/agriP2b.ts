import type { Locale } from '../i18n/types';

function bcp47(locale: Locale): string {
  return locale === 'pt-BR' ? 'pt-BR' : 'en';
}

/** Anos PAM cobertos pelos JSONs processados (sem inventar anos). */
export const PAM_YEARS: readonly string[] = [
  '2018',
  '2019',
  '2020',
  '2021',
  '2022',
  '2023',
  '2024',
  '2025',
];

/**
 * Culturas de grãos com `average_yield_kg_per_ha` em escala comparável
 * (chaves estáveis do payload unificado `pam_unified.json`).
 * Cana-de-açúcar/tubérculos/mandioca ficam fora (ordem de grandeza
 * 5–20× maior achataria o eixo) — nota de rodapé nos componentes.
 */
export const PAM_GRAIN_KEYS: readonly string[] = [
  'soybean',
  'corn',
  'rice',
  'wheat',
  'cotton',
  'peanut',
  'oat',
];

/**
 * Entrada de cultura do payload unificado `pam_unified.json`: série
 * numérica única (chaves EN estáveis) + dicionário de nomes `{en, pt}`.
 */
export interface PamCropEntry {
  code: string;
  /** Nome EN (ex. `"Soybean (grain)"`). */
  name: string;
  /** Nome PT (ex. `"Soja (em grão)"`). */
  nome: string;
  production_quantity_tonnes?: Record<string, number>;
  harvested_area_hectares?: Record<string, number>;
  average_yield_kg_per_ha?: Record<string, number>;
}

export type PamProduction = Record<string, PamCropEntry>;

/** Raiz de `pam_unified.json` (metadados bilíngues + culturas + resumo). */
export interface PamUnified {
  metadata?: {
    period_range?: string | null;
    periodicity?: { pt?: string | null; en?: string | null } | null;
    survey?: { pt?: string | null; en?: string | null } | null;
    [key: string]: unknown;
  };
  crops?: PamProduction;
  summary_annual?: Record<
    string,
    {
      total_harvested_area_hectares?: number;
      main_crops?: string[];
      total_production_value_billion_reais?: number;
      [key: string]: unknown;
    }
  >;
}

/** Nome da cultura no locale ativo (dicionário `{en, pt}`, sem re-fetch). */
export function pamCropName(entry: PamCropEntry, locale: Locale): string {
  if (locale === 'pt-BR') return entry.nome || entry.name;
  return entry.name || entry.nome;
}

export interface YieldSeries {
  name: string;
  x: string[];
  y: (number | null)[];
}

/**
 * Série de rendimento médio (kg/ha) por cultura PAM — só anos presentes
 * no JSON (ausente vira `null`, nunca zero inventado). Nome localizado
 * via dicionário `{en, pt}` do payload unificado.
 */
export function buildPamYieldSeries(
  production: PamProduction | undefined,
  cropKeys: readonly string[],
  years: readonly string[],
  locale: Locale = 'pt-BR',
): YieldSeries[] {
  if (production === undefined) return [];
  return cropKeys.flatMap((key): YieldSeries[] => {
    const entry = production[key];
    const yields = entry?.average_yield_kg_per_ha;
    if (entry === undefined || yields === undefined) return [];
    return [
      {
        name: pamCropName(entry, locale) || key,
        x: [...years],
        y: years.map((year) => {
          const v = yields[year];
          return typeof v === 'number' ? v : null;
        }),
      },
    ];
  });
}

export interface ConabSeason {
  production: number;
  area: number;
  productivity: number;
}

export interface ConabCrop {
  name: string;
  scientific_name?: string;
  production_data?: Record<string, ConabSeason>;
}

export type ConabCrops = Record<string, ConabCrop>;

/** Variação percentual (null quando a base é 0/ausente). */
export function deltaPct(current: number, previous: number): number | null {
  if (previous === 0) return null;
  return ((current - previous) / Math.abs(previous)) * 100;
}

/** `+10,3%` / `-2.0%` no locale ativo; `–` sem base. */
export function formatDeltaPct(delta: number | null, locale: Locale): string {
  if (delta === null || !Number.isFinite(delta)) return '–';
  const sign = delta > 0 ? '+' : delta < 0 ? '-' : '';
  const abs = Math.abs(delta).toLocaleString(bcp47(locale), {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  });
  return `${sign}${abs}%`;
}

export interface SeasonCloseRow {
  key: string;
  name: string;
  areaPrev: number;
  areaNext: number;
  prodPrev: number;
  prodNext: number;
  deltaArea: number | null;
  deltaProd: number | null;
}

/**
 * Fechamento safra anterior × safra atual (CONAB) — top N por produção da
 * safra anterior, só safras presentes no JSON.
 */
export function buildSeasonClose(
  crops: ConabCrops | undefined,
  prevSeason: string,
  nextSeason: string,
  topN: number,
): SeasonCloseRow[] {
  if (crops === undefined) return [];
  const rows: SeasonCloseRow[] = [];
  for (const [key, crop] of Object.entries(crops)) {
    const prev = crop.production_data?.[prevSeason];
    const next = crop.production_data?.[nextSeason];
    if (prev === undefined || next === undefined) continue;
    rows.push({
      key,
      name: crop.name,
      areaPrev: prev.area,
      areaNext: next.area,
      prodPrev: prev.production,
      prodNext: next.production,
      deltaArea: deltaPct(next.area, prev.area),
      deltaProd: deltaPct(next.production, prev.production),
    });
  }
  rows.sort((a, b) => b.prodPrev - a.prodPrev);
  return rows.slice(0, topN);
}
