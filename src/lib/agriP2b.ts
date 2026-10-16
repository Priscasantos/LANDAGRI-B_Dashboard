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
 * Culturas de grãos com `rendimento_medio_kg_por_ha` em escala comparável.
 * Cana-de-açúcar/tubérculos/mandioca ficam fora (ordem de grandeza
 * 5–20× maior achataria o eixo) — nota de rodapé nos componentes.
 */
export const PAM_GRAIN_KEYS: readonly string[] = [
  'soja',
  'milho',
  'arroz',
  'trigo',
  'algodao',
  'amendoim',
  'aveia',
];

export interface PamCropEntry {
  nome: string;
  codigo: string;
  quantidade_produzida_toneladas?: Record<string, number>;
  area_colhida_hectares?: Record<string, number>;
  rendimento_medio_kg_por_ha?: Record<string, number>;
}

export type PamProduction = Record<string, PamCropEntry>;

export interface YieldSeries {
  name: string;
  x: string[];
  y: (number | null)[];
}

/**
 * Série de rendimento médio (kg/ha) por cultura PAM — só anos presentes
 * no JSON (ausente vira `null`, nunca zero inventado).
 */
export function buildPamYieldSeries(
  production: PamProduction | undefined,
  cropKeys: readonly string[],
  years: readonly string[],
): YieldSeries[] {
  if (production === undefined) return [];
  return cropKeys.flatMap((key): YieldSeries[] => {
    const entry = production[key];
    const yields = entry?.rendimento_medio_kg_por_ha;
    if (entry === undefined || yields === undefined) return [];
    return [
      {
        name: entry.nome || key,
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
