import { describe, it, expect } from 'vitest';
import {
  aggregateShares,
  aggregateSharesByGroup,
  bulletinSlotForMonth,
  currentCalendarMonth,
  formatShareTip,
  recencyOf,
  resolveShareMode,
  toCalendarRecords,
  topUfsWithOverflow,
  type MonthShare,
} from '../../lib/calendarShare';
import type { CalendarAvailability } from '../../types/calendar';

function rec(cropId: string, region: string, month: number, code: 'P' | 'H' | 'PH' | ''): CalendarAvailability {
  const plantingPct = code === 'P' ? 100 : code === 'PH' ? 50 : 0;
  const harvestPct = code === 'H' ? 100 : code === 'PH' ? 50 : 0;
  return {
    cropId,
    month,
    region,
    plantingPct,
    harvestPct,
    source: 'CONAB',
    vintage: 'conab_crop_calendar.csv',
    updatedAt: '2026-10-16',
  };
}

describe('calendarShare aggregation (Fase 2)', () => {
  it('converte linhas tipadas em registros sem parse ad-hoc', () => {
    const records = toCalendarRecords(
      [{ crop: 'Cotton', uf: 'MT', months: ['P', '', '', '', '', '', '', 'H', '', '', '', ''] }],
      { vintage: 'test.csv', updatedAt: '2026-10-16' },
    );
    expect(records).toHaveLength(12);
    // Slot 0 do boletim = outubro → mês 10 com plantio 100%.
    expect(records.find((r) => r.month === 10)).toMatchObject({ plantingPct: 100, harvestPct: 0 });
    expect(records.find((r) => r.month === 5)).toMatchObject({ plantingPct: 0, harvestPct: 100 });
  });

  it('agrega % de UFs ativas por mês (não binário 0/1)', () => {
    const records = [
      rec('Cotton', 'MT', 1, 'P'),
      rec('Cotton', 'GO', 1, ''),
      rec('Cotton', 'BA', 1, 'H'),
      rec('Cotton', 'MT', 2, ''),
    ];
    const months: MonthShare[] = aggregateShares(records);
    expect(months).toHaveLength(12);
    const jan = months.find((m) => m.month === 1);
    expect(jan?.totalUfs).toBe(3);
    expect(jan?.activeUfs).toBe(2);
    expect(jan?.pctActive).toBeCloseTo((2 / 3) * 100, 5);
    expect(jan?.pctPlanting).toBeCloseTo((1 / 3) * 100, 5);
    expect(jan?.pctHarvest).toBeCloseTo((1 / 3) * 100, 5);
    expect(jan?.plantingList).toEqual(['MT']);
    expect(jan?.harvestList).toEqual(['BA']);
  });

  it('preserva edges 0% e 100% sem divisão por zero', () => {
    const empty = aggregateShares([]);
    for (const m of empty) {
      expect(m.pctActive).toBe(0);
      expect(m.totalUfs).toBe(0);
    }
    const full = aggregateShares([rec('Cotton', 'MT', 6, 'PH'), rec('Cotton', 'GO', 6, 'P')]);
    const jun = full.find((m) => m.month === 6);
    expect(jun?.pctActive).toBe(100);
    expect(jun?.pctPlanting).toBe(100);
    expect(jun?.pctHarvest).toBe(50);
  });

  it('agrupa por cultura/região mantendo % por mês', () => {
    const records = [rec('Cotton', 'MT', 1, 'P'), rec('Soybean', 'MT', 1, 'H'), rec('Cotton', 'GO', 1, '')];
    const byCrop = aggregateSharesByGroup(records, (r) => r.cropId);
    expect(byCrop.get('Cotton')?.find((m) => m.month === 1)?.pctActive).toBe(50);
    expect(byCrop.get('Soybean')?.find((m) => m.month === 1)?.pctActive).toBe(100);
  });

  it('usa % de área quando disponível, senão fallback % de UFs rotulado', () => {
    expect(resolveShareMode([rec('Cotton', 'MT', 1, 'P')])).toBe('uf');
    const withArea = [
      { ...rec('Cotton', 'MT', 1, 'P'), areaSharePct: 80 },
      { ...rec('Cotton', 'GO', 1, ''), areaSharePct: 20 },
    ];
    expect(resolveShareMode(withArea)).toBe('area');
    const jan = aggregateShares(withArea).find((m) => m.month === 1);
    expect(jan?.mode).toBe('area');
    expect(jan?.pctActive).toBe(80);
  });

  it('lista top-N UFs com overflow para tooltips', () => {
    const out = topUfsWithOverflow(['BA', 'GO', 'MG', 'MS', 'MT', 'PR', 'SP'], 5);
    expect(out.top).toHaveLength(5);
    expect(out.overflow).toBe(2);
    expect(topUfsWithOverflow(['MT'], 5).overflow).toBe(0);
  });

  it('expõe mês atual civil e recência da fonte', () => {
    const now = new Date().getMonth() + 1;
    expect(currentCalendarMonth()).toBe(now);
    const records = [rec('Cotton', 'MT', 1, 'P')];
    expect(recencyOf(records)).toMatchObject({
      source: 'CONAB',
      vintage: 'conab_crop_calendar.csv',
      updatedAt: '2026-10-16',
    });
    expect(recencyOf([])).toBeNull();
  });

  it('mapeia mês civil para slot do boletim (Out=0 … Set=11)', () => {
    expect(bulletinSlotForMonth(10)).toBe(0);
    expect(bulletinSlotForMonth(1)).toBe(3);
    expect(bulletinSlotForMonth(9)).toBe(11);
  });

  it('formata tooltip com % + top-N UFs e overflow', () => {
    const months = aggregateShares([
      rec('Cotton', 'BA', 1, 'P'),
      rec('Cotton', 'GO', 1, 'P'),
      rec('Cotton', 'MT', 1, 'H'),
    ]);
    const jan = months.find((m) => m.month === 1);
    if (jan === undefined) throw new Error('mês 1 ausente');
    const tip = formatShareTip('Cotton · Jan', jan, {
      activeUfs: 'UFs ativas',
      planting: 'Plantio',
      harvest: 'Colheita',
      more: (k) => `+${k} outras`,
    });
    expect(tip).toContain('Cotton · Jan');
    expect(tip).toContain('100%');
    expect(tip).toContain('BA, GO');
    expect(tip).toContain('MT');
    const crowded = formatShareTip(
      'X',
      { ...jan, plantingList: ['A', 'B', 'C', 'D', 'E', 'F', 'G'] },
      {
        activeUfs: 'UFs ativas',
        planting: 'Plantio',
        harvest: 'Colheita',
        more: (k) => `+${k} outras`,
      },
      5,
    );
    expect(crowded).toContain('+2 outras');
    expect(crowded).not.toContain('F, G');
  });
});
