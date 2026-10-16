/**
 * Fase 2 — agregação dado→visual para calendários de disponibilidade.
 *
 * Troca a agregação binária (0/1 por UF) por % de UFs ativas e % de área:
 * - `pctActive/pctPlanting/pctHarvest` por mês civil (1–12), 0–100.
 * - Quando todo registro carrega `areaSharePct`, pondera por área
 *   (`mode: 'area'`); sem área por UF (ex. PAM nacional), usa contagem de
 *   UFs (`mode: 'uf'`) — o UI rotula o fallback explicitamente.
 * - Só consome o schema tipado (`CalendarAvailability` via
 *   `normalizeCalendarRows`); nenhum parse ad-hoc de `P`/`H` aqui.
 */
import {
  normalizeCalendarRows,
  type CalendarAvailability,
  type ConabCalendarRow,
  type NormalizeCalendarOptions,
} from '../types/calendar';

export type ShareMode = 'uf' | 'area';

export interface MonthShare {
  /** Mês civil 1–12. */
  month: number;
  /** UFs distintas com registro no mês. */
  totalUfs: number;
  /** UFs com plantio ou colheita no mês. */
  activeUfs: number;
  plantingUfs: number;
  harvestUfs: number;
  /** % ativas / plantio / colheita (0–100). */
  pctActive: number;
  pctPlanting: number;
  pctHarvest: number;
  /** Listas ordenadas de siglas UF (para tooltips top-N + overflow). */
  activeList: string[];
  plantingList: string[];
  harvestList: string[];
  mode: ShareMode;
}

export interface TopUfs {
  top: string[];
  overflow: number;
}

export interface Recency {
  source: string;
  vintage: string;
  updatedAt: string;
}

export const TOOLTIP_TOP_UFS = 5;

/** Normaliza linhas tipadas CONAB em registros canônicos (schema Fase 1). */
export function toCalendarRecords(
  rows: ConabCalendarRow[],
  options: NormalizeCalendarOptions = {},
): CalendarAvailability[] {
  return normalizeCalendarRows(rows, options);
}

/** `true` quando o mês tem atividade (plantio ou colheita). */
function isActive(r: CalendarAvailability): boolean {
  return r.plantingPct > 0 || r.harvestPct > 0;
}

/**
 * Resolve o modo de participação: `'area'` só quando TODOS os registros
 * trazem `areaSharePct` numérico (ponderação honesta); senão `'uf'`.
 */
export function resolveShareMode(records: CalendarAvailability[]): ShareMode {
  if (records.length === 0) return 'uf';
  return records.every(
    (r) => typeof r.areaSharePct === 'number' && Number.isFinite(r.areaSharePct),
  )
    ? 'area'
    : 'uf';
}

function emptyMonth(month: number, mode: ShareMode): MonthShare {
  return {
    month,
    totalUfs: 0,
    activeUfs: 0,
    plantingUfs: 0,
    harvestUfs: 0,
    pctActive: 0,
    pctPlanting: 0,
    pctHarvest: 0,
    activeList: [],
    plantingList: [],
    harvestList: [],
    mode,
  };
}

function buildMonthShare(month: number, records: CalendarAvailability[], mode: ShareMode): MonthShare {
  if (records.length === 0) return emptyMonth(month, mode);
  const active = records.filter(isActive);
  const planting = records.filter((r) => r.plantingPct > 0);
  const harvest = records.filter((r) => r.harvestPct > 0);
  const uniq = (list: CalendarAvailability[]): string[] =>
    [...new Set(list.map((r) => r.region))].sort();

  if (mode === 'area') {
    const totalArea = records.reduce((sum, r) => sum + (r.areaSharePct ?? 0), 0);
    const pct = (list: CalendarAvailability[]): number =>
      totalArea > 0
        ? (list.reduce((sum, r) => sum + (r.areaSharePct ?? 0), 0) / totalArea) * 100
        : 0;
    return {
      month,
      totalUfs: uniq(records).length,
      activeUfs: uniq(active).length,
      plantingUfs: uniq(planting).length,
      harvestUfs: uniq(harvest).length,
      pctActive: pct(active),
      pctPlanting: pct(planting),
      pctHarvest: pct(harvest),
      activeList: uniq(active),
      plantingList: uniq(planting),
      harvestList: uniq(harvest),
      mode,
    };
  }

  const total = records.length;
  return {
    month,
    totalUfs: uniq(records).length,
    activeUfs: uniq(active).length,
    plantingUfs: uniq(planting).length,
    harvestUfs: uniq(harvest).length,
    pctActive: total > 0 ? (uniq(active).length / uniq(records).length) * 100 : 0,
    pctPlanting: total > 0 ? (uniq(planting).length / uniq(records).length) * 100 : 0,
    pctHarvest: total > 0 ? (uniq(harvest).length / uniq(records).length) * 100 : 0,
    activeList: uniq(active),
    plantingList: uniq(planting),
    harvestList: uniq(harvest),
    mode,
  };
}

/**
 * Agrega registros em 12 `MonthShare` (mês civil 1–12, sempre 12 entradas —
 * meses sem registro viram 0% explícito, nunca lacuna silenciosa).
 */
export function aggregateShares(records: CalendarAvailability[]): MonthShare[] {
  const mode = resolveShareMode(records);
  const byMonth = new Map<number, CalendarAvailability[]>();
  for (const r of records) {
    const list = byMonth.get(r.month) ?? [];
    list.push(r);
    byMonth.set(r.month, list);
  }
  return Array.from({ length: 12 }, (_, i) => buildMonthShare(i + 1, byMonth.get(i + 1) ?? [], mode));
}

/** Agrega por grupo (cultura, região, UF…) → 12 `MonthShare` por chave. */
export function aggregateSharesByGroup(
  records: CalendarAvailability[],
  groupKey: (record: CalendarAvailability) => string,
): Map<string, MonthShare[]> {
  const groups = new Map<string, CalendarAvailability[]>();
  for (const r of records) {
    const key = groupKey(r);
    const list = groups.get(key) ?? [];
    list.push(r);
    groups.set(key, list);
  }
  const out = new Map<string, MonthShare[]>();
  for (const [key, list] of groups) out.set(key, aggregateShares(list));
  return out;
}

/** Fatia a lista de UFs em top-N + overflow ("+k outras"). */
export function topUfsWithOverflow(ufs: string[], topN: number = TOOLTIP_TOP_UFS): TopUfs {
  return { top: ufs.slice(0, topN), overflow: Math.max(ufs.length - topN, 0) };
}

/** Mês civil atual (1–12) para o marcador de mês nos gráficos. */
export function currentCalendarMonth(now: Date = new Date()): number {
  return now.getMonth() + 1;
}

/**
 * Mês civil (1–12) → slot do boletim CONAB (0 = outubro … 11 = setembro).
 * Inverso de `bulletinIndexToMonth` (posição do mês atual no eixo Out→Set).
 */
export function bulletinSlotForMonth(month: number): number {
  return (month - 10 + 12) % 12;
}

export interface ShareTipLabels {
  activeUfs: string;
  planting: string;
  harvest: string;
  more: (overflow: number) => string;
}

/**
 * Tooltip HTML de célula/barra: título + % ativas (n/total) + listas P/H
 * (top-N + "+k outras"). Rótulos injetados pelo chamador (i18n resolvido
 * no componente); valores sempre arredondados em % inteira.
 */
export function formatShareTip(
  title: string,
  share: MonthShare,
  labels: ShareTipLabels,
  topN: number = TOOLTIP_TOP_UFS,
): string {
  const formatList = (list: string[]): string => {
    const { top, overflow } = topUfsWithOverflow(list, topN);
    const base = top.join(', ') || '–';
    return overflow > 0 ? `${base} ${labels.more(overflow)}` : base;
  };
  return (
    `<b>${title}</b><br>` +
    `${labels.activeUfs}: ${Math.round(share.pctActive)}% (${share.activeUfs}/${share.totalUfs})<br>` +
    `${labels.planting}: ${formatList(share.plantingList)}<br>` +
    `${labels.harvest}: ${formatList(share.harvestList)}`
  );
}

/** Recência da fonte a partir do primeiro registro (null sem dados). */
export function recencyOf(records: CalendarAvailability[]): Recency | null {
  const first = records[0];
  if (first === undefined) return null;
  return { source: first.source, vintage: first.vintage, updatedAt: first.updatedAt };
}
