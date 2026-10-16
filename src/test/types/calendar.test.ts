import { describe, it, expect } from 'vitest';
import {
  CalendarActivity,
  activityFromCode,
  bulletinIndexToMonth,
  normalizeCalendarRows,
  type ConabCalendarRow,
} from '../../types/calendar';

describe('CalendarAvailability schema (Fase 1)', () => {
  it('normaliza o triplo P/H para enum + percentuais', () => {
    expect(activityFromCode('P')).toEqual({ activity: CalendarActivity.Planting, plantingPct: 100, harvestPct: 0 });
    expect(activityFromCode('H')).toEqual({ activity: CalendarActivity.Harvest, plantingPct: 0, harvestPct: 100 });
    // PH = plantio E colheita no mesmo mês: divide 50/50 (soma 100).
    expect(activityFromCode('PH')).toEqual({ activity: CalendarActivity.Both, plantingPct: 50, harvestPct: 50 });
    expect(activityFromCode('')).toEqual({ activity: CalendarActivity.None, plantingPct: 0, harvestPct: 0 });
    expect(activityFromCode('ph')).toEqual(activityFromCode('PH'));
    expect(activityFromCode('X')).toEqual({ activity: CalendarActivity.None, plantingPct: 0, harvestPct: 0 });
  });

  it('mapeia slot do boletim (Out→Set) para mês civil 1-12', () => {
    expect(bulletinIndexToMonth(0)).toBe(10); // October
    expect(bulletinIndexToMonth(1)).toBe(11);
    expect(bulletinIndexToMonth(2)).toBe(12);
    expect(bulletinIndexToMonth(3)).toBe(1); // January
    expect(bulletinIndexToMonth(11)).toBe(9); // September
  });

  it('expande linhas tipadas em 12 registros canônicos', () => {
    const rows: ConabCalendarRow[] = [
      { crop: 'Cotton', uf: 'RO', months: ['', '', '', 'P', 'P', '', '', '', 'H', 'H', 'H', ''] },
    ];
    const out = normalizeCalendarRows(rows, { vintage: 'test.csv', updatedAt: '2026-10-16' });
    expect(out).toHaveLength(12);
    expect(new Set(out.map((r) => r.month))).toEqual(new Set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]));
    // Janeiro (slot 3) = plantio 100%; Junho (slot 8) = colheita 100%.
    expect(out.find((r) => r.month === 1)).toMatchObject({
      cropId: 'Cotton',
      region: 'RO',
      plantingPct: 100,
      harvestPct: 0,
      source: 'CONAB',
      vintage: 'test.csv',
      updatedAt: '2026-10-16',
    });
    expect(out.find((r) => r.month === 6)).toMatchObject({ plantingPct: 0, harvestPct: 100 });
    // Invariante: soma por mês é 0 ou 100; nenhum `;` vaza para o payload.
    for (const r of out) {
      expect([0, 100]).toContain(r.plantingPct + r.harvestPct);
    }
    expect(JSON.stringify(out)).not.toContain(';');
  });

  it('descarta linhas sem cultura/UF ou sem 12 meses (sem zerar inventado)', () => {
    const rows: ConabCalendarRow[] = [
      { crop: '', uf: 'RO', months: Array(12).fill('P') },
      { crop: 'Cotton', uf: '', months: Array(12).fill('P') },
      { crop: 'Cotton', uf: 'TO', months: ['P'] },
    ];
    expect(normalizeCalendarRows(rows)).toHaveLength(0);
  });
});
