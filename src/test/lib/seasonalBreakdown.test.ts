import { describe, it, expect } from 'vitest';
import {
  formatBreakdownTip,
  summarizeActivityByGroup,
  type ShareTipLabels,
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

const labels: ShareTipLabels = {
  activeUfs: 'UFs ativas',
  planting: 'Plantio',
  harvest: 'Colheita',
  more: (k) => `+${k} outras`,
};

describe('seasonal breakdown por cultura/região (só agregação, sem invenção)', () => {
  it('conta células UF×mês com P/H por grupo', () => {
    const records = [
      rec('Cotton', 'MT', 10, 'P'),
      rec('Cotton', 'MT', 11, 'P'),
      rec('Cotton', 'GO', 10, ''),
      rec('Soybean', 'MT', 10, 'H'),
    ];
    const byCrop = summarizeActivityByGroup(records, (r) => r.cropId);
    const cotton = byCrop.find((b) => b.key === 'Cotton');
    expect(cotton).toMatchObject({ totalCells: 3, plantingCells: 2, harvestCells: 0 });
    expect(cotton?.pctPlanting).toBeCloseTo((2 / 3) * 100, 5);
    expect(cotton?.pctHarvest).toBe(0);
    expect(cotton?.plantingUfs).toEqual(['MT']);
    expect(cotton?.activeUfs).toEqual(['MT']);
  });

  it('agrupa por região via UF→região resolvida pelo chamador', () => {
    const ufToRegion: Record<string, string> = { MT: 'Central-West', GO: 'Central-West', BA: 'Northeast' };
    const records = [rec('Cotton', 'MT', 10, 'P'), rec('Cotton', 'GO', 10, 'H'), rec('Cotton', 'BA', 10, '')];
    const byRegion = summarizeActivityByGroup(records, (r) => ufToRegion[r.region] ?? r.region);
    const cw = byRegion.find((b) => b.key === 'Central-West');
    expect(cw).toMatchObject({ totalCells: 2, plantingCells: 1, harvestCells: 1 });
    expect(cw?.pctPlanting).toBe(50);
    expect(cw?.plantingUfs).toEqual(['MT']);
    expect(cw?.harvestUfs).toEqual(['GO']);
  });

  it('grupo sem atividade zera % sem divisão por zero', () => {
    const byCrop = summarizeActivityByGroup([rec('Cotton', 'MT', 10, '')], (r) => r.cropId);
    expect(byCrop[0]).toMatchObject({ pctPlanting: 0, pctHarvest: 0, plantingUfs: [], harvestUfs: [] });
    expect(summarizeActivityByGroup([], (r) => r.cropId)).toEqual([]);
  });

  it('tooltip do breakdown traz % + UFs com overflow honesto', () => {
    const breakdown = {
      key: 'Cotton',
      totalCells: 12,
      plantingCells: 6,
      harvestCells: 3,
      pctPlanting: 50,
      pctHarvest: 25,
      plantingUfs: ['BA', 'GO', 'MA', 'MT', 'PI', 'TO'],
      harvestUfs: ['MT'],
      activeUfs: ['BA', 'GO', 'MA', 'MT', 'PI', 'TO'],
    };
    const tip = formatBreakdownTip('Algodão', breakdown, labels);
    expect(tip).toContain('<b>Algodão</b>');
    expect(tip).toContain('Plantio: 50%');
    expect(tip).toContain('Colheita: 25%');
    expect(tip).toContain('MT');
    expect(tip).toContain('+1 outras');
  });

  it('fatia do tooltip isola plantio ou colheita por série', () => {
    const breakdown = {
      key: 'Cotton',
      totalCells: 4,
      plantingCells: 2,
      harvestCells: 2,
      pctPlanting: 50,
      pctHarvest: 50,
      plantingUfs: ['MT'],
      harvestUfs: ['GO'],
      activeUfs: ['GO', 'MT'],
    };
    const plantingOnly = formatBreakdownTip('Algodão', breakdown, labels, 5, 'planting');
    expect(plantingOnly).toContain('Plantio: 50% (MT)');
    expect(plantingOnly).not.toContain('Colheita');
    const harvestOnly = formatBreakdownTip('Algodão', breakdown, labels, 5, 'harvest');
    expect(harvestOnly).toContain('Colheita: 50% (GO)');
    expect(harvestOnly).not.toContain('Plantio');
  });
});
