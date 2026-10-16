import { describe, it, expect } from 'vitest';
import { aggregateSharesWithMode } from '../../lib/calendarShare';
import type { CalendarAvailability } from '../../types/calendar';

function rec(cropId: string, region: string, month: number, areaSharePct?: number): CalendarAvailability {
  return {
    cropId,
    month,
    region,
    plantingPct: 100,
    harvestPct: 0,
    ...(areaSharePct === undefined ? {} : { areaSharePct }),
    source: 'CONAB',
    vintage: 'conab_crop_calendar.csv',
    updatedAt: '2026-10-16',
  };
}

describe('aggregateSharesWithMode (toggle % UFs vs % área)', () => {
  it('sem areaSharePct, pedido de área cai para UFs rotulado (nunca inventa área)', () => {
    const records = [rec('Cotton', 'MT', 1), rec('Cotton', 'GO', 1)];
    const out = aggregateSharesWithMode(records, 'area');
    expect(out.effective).toBe('uf');
    expect(out.hasArea).toBe(false);
    expect(out.shares.find((m) => m.month === 1)?.pctPlanting).toBe(100);
  });

  it('com areaSharePct em tudo, área pondera de verdade e vira default', () => {
    const records = [rec('Cotton', 'MT', 1, 80), rec('Cotton', 'GO', 1, 20)];
    const out = aggregateSharesWithMode(records, 'area');
    expect(out.effective).toBe('area');
    expect(out.hasArea).toBe(true);
    const uf = aggregateSharesWithMode(records, 'uf');
    expect(uf.effective).toBe('uf');
    // % área (80/20 sobre uma UF ativa cada) difere da contagem simples quando
    // só parte das UFs está ativa: adiciona GO inativa no mês 2.
    const mixed = [rec('Cotton', 'MT', 2, 80), { ...rec('Cotton', 'GO', 2, 20), plantingPct: 0, harvestPct: 0 }];
    const area = aggregateSharesWithMode(mixed, 'area');
    expect(area.shares.find((m) => m.month === 2)?.pctPlanting).toBeCloseTo(80, 5);
    const byUf = aggregateSharesWithMode(mixed, 'uf');
    expect(byUf.shares.find((m) => m.month === 2)?.pctPlanting).toBeCloseTo(50, 5);
  });

  it('modo explícito UFs continua honesto mesmo com área disponível', () => {
    const records = [rec('Cotton', 'MT', 3, 90), rec('Cotton', 'GO', 3, 10)];
    const out = aggregateSharesWithMode(records, 'uf');
    expect(out.effective).toBe('uf');
    expect(out.shares.find((m) => m.month === 3)?.mode).toBe('uf');
  });
});
