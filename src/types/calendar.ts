/**
 * Canonical crop-calendar availability schema (Fase 1 — data sanitization).
 *
 * Replaces the legacy `;`-joined single-key rows
 * (`"Crop type;Federation Unit;October;…"` + `split(';')` consumers) with a
 * typed row per crop × UF × calendar month. The triple P/H encoding is
 * normalized to an enum plus explicit percentages so charts never parse
 * raw codes again.
 *
 * Source: CONAB crop calendar (`data/csv/conab_crop_calendar.csv`,
 * October→September bulletin order).
 */

/**
 * Canonical monthly agricultural activity (normalized P/H triple).
 * Const object (not `enum`) — `erasableSyntaxOnly` is enabled.
 */
export const CalendarActivity = {
  None: 'none',
  Planting: 'planting',
  Harvest: 'harvest',
  Both: 'both',
} as const;

export type CalendarActivity = (typeof CalendarActivity)[keyof typeof CalendarActivity];

/**
 * Typed CONAB calendar row as emitted by `scripts/preprocess-data.mjs`.
 * `months` runs October→September (bulletin order), one raw code per slot.
 */
export interface ConabCalendarRow {
  crop: string;
  uf: string;
  months: string[];
}

/** Typed CONAB availability row as emitted by `scripts/preprocess-data.mjs`. */
export interface ConabAvailabilityRow {
  crop: string;
  uf: string;
  anos_1s: string[];
  anos_2s: string[];
  is_long_aggregate: boolean;
}

/**
 * Canonical availability record: one crop × UF × calendar month.
 */
export interface CalendarAvailability {
  /** Stable crop key (CONAB EN label, e.g. `"Cotton"`). */
  cropId: string;
  /** Calendar month 1–12 (January = 1). */
  month: number;
  /** Region: UF sigla (`"BR"` = national aggregate). */
  region: string;
  /** Planting share of the month's agricultural activity, 0–100. */
  plantingPct: number;
  /** Harvest share of the month's agricultural activity, 0–100. */
  harvestPct: number;
  /** Optional share of the crop's national area in this UF (%). */
  areaSharePct?: number;
  /** Data source (e.g. `"CONAB"`). */
  source: string;
  /** Source vintage (e.g. `"conab_crop_calendar.csv"`). */
  vintage: string;
  /** Normalization date (ISO `YYYY-MM-DD`). */
  updatedAt: string;
}

/** Bulletin column order: `months[0]` = October … `months[11]` = September. */
export const CALENDAR_MONTH_ORDER = [
  'October',
  'November',
  'December',
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
] as const;

/** Bulletin slot index → calendar month (0 = October → 10). */
export function bulletinIndexToMonth(index: number): number {
  return ((9 + index) % 12) + 1;
}

export interface NormalizedActivity {
  activity: CalendarActivity;
  plantingPct: number;
  harvestPct: number;
}

/**
 * Normalize one raw month code (`P`/`H`/`PH`/`""`) to enum + percentages.
 *
 * `PH` means planting AND harvest both occur that month, so the activity
 * share splits 50/50 (invariant: `plantingPct + harvestPct` is 0 or 100).
 * Unknown/blank codes → `None` (never invented activity).
 */
export function activityFromCode(code: string): NormalizedActivity {
  const v = (code || '').trim().toUpperCase();
  if (v === 'PH') return { activity: CalendarActivity.Both, plantingPct: 50, harvestPct: 50 };
  if (v === 'P') return { activity: CalendarActivity.Planting, plantingPct: 100, harvestPct: 0 };
  if (v === 'H') return { activity: CalendarActivity.Harvest, plantingPct: 0, harvestPct: 100 };
  return { activity: CalendarActivity.None, plantingPct: 0, harvestPct: 0 };
}

export interface NormalizeCalendarOptions {
  source?: string;
  vintage?: string;
  updatedAt?: string;
}

/**
 * Expand typed calendar rows into canonical `CalendarAvailability` records
 * (12 per row, October slot → month 10). Rows without crop/UF or without a
 * full 12-slot `months` array are skipped — never padded with zeros.
 */
export function normalizeCalendarRows(
  rows: ConabCalendarRow[],
  options: NormalizeCalendarOptions = {},
): CalendarAvailability[] {
  const {
    source = 'CONAB',
    vintage = 'conab_crop_calendar.csv',
    updatedAt = new Date().toISOString().slice(0, 10),
  } = options;
  const out: CalendarAvailability[] = [];
  for (const row of rows) {
    const cropId = (row.crop || '').trim();
    const region = (row.uf || '').trim();
    if (!cropId || !region) continue;
    if (!Array.isArray(row.months) || row.months.length < 12) continue;
    row.months.slice(0, 12).forEach((code, i) => {
      const { plantingPct, harvestPct } = activityFromCode(code);
      out.push({
        cropId,
        month: bulletinIndexToMonth(i),
        region,
        plantingPct,
        harvestPct,
        source,
        vintage,
        updatedAt,
      });
    });
  }
  return out;
}
