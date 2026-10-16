import { describe, it, expect } from 'vitest';
import {
  MAX_PHENO_LANES,
  buildPhenoModel,
  seasonLabelForDate,
  type ConabPhenoRow,
} from '../../lib/phenoGantt';

const regions = { MT: 'Central-West', GO: 'Central-West', PR: 'South' };

function row(crop: string, uf: string, months: string[]): ConabPhenoRow {
  const full = [...months];
  while (full.length < 12) full.push('');
  return { crop, uf, months: full.slice(0, 12) };
}

describe('phenoGantt segments (Gaia: lanes P/H por cultura-região)', () => {
  it('cria duas lanes P/H por cultura-região (não por UF)', () => {
    const model = buildPhenoModel(
      [row('Soybean', 'MT', ['P', 'P', '', '', '', '', '', '', 'H', 'H', '', '']), row('Soybean', 'GO', ['', 'P', '', '', '', '', '', '', '', 'H', '', ''])],
      regions,
    );
    const laneIds = model.lanes.map((l) => l.id).sort();
    expect(laneIds).toEqual(['Soybean¦Central-West¦H', 'Soybean¦Central-West¦P']);
  });

  it('nunca colapsa hiato: meses ativos disjuntos viram segmentos separados', () => {
    const model = buildPhenoModel([row('Cotton', 'MT', ['P', 'P', '', '', '', 'P', '', '', '', '', '', ''])], regions);
    const pLane = model.lanes.find((l) => l.kind === 'P');
    expect(pLane).toBeDefined();
    const segs = model.segments.filter((s) => s.laneId === pLane?.id);
    expect(segs).toHaveLength(2);
    expect([segs[0]?.start, segs[0]?.end]).toEqual([0, 2]);
    expect([segs[1]?.start, segs[1]?.end]).toEqual([5, 6]);
  });

  it('PH vira faixa própria com flag ph (hachura + tooltip de 2º ciclo)', () => {
    const model = buildPhenoModel([row('Corn (2nd harvest)', 'PR', ['P', 'PH', 'P', '', '', '', '', 'H', '', '', '', ''])], regions);
    const pSegs = model.segments.filter((s) => s.laneId.endsWith('¦P')).sort((a, b) => a.start - b.start);
    expect(pSegs).toHaveLength(3);
    expect(pSegs[1]).toMatchObject({ start: 1, end: 2, ph: true, phUfs: ['PR'] });
    expect(pSegs[0]).toMatchObject({ ph: false });
    const hSegs = model.segments.filter((s) => s.laneId.endsWith('¦H'));
    // PH conta nas duas lanes: [1,2) hachurado + [7,8) simples.
    expect(hSegs).toHaveLength(2);
    expect(hSegs[0]).toMatchObject({ start: 1, end: 2, ph: true });
    expect(hSegs[1]).toMatchObject({ start: 7, end: 8, ph: false });
  });

  it('união por região lista UFs ativas por slot (tooltip honesto)', () => {
    const model = buildPhenoModel(
      [row('Soybean', 'MT', ['P', '', '', '', '', '', '', '', '', '', '', '']), row('Soybean', 'GO', ['P', '', '', '', '', '', '', '', '', '', '', ''])],
      regions,
    );
    const seg = model.segments.find((s) => s.laneId.endsWith('¦P'));
    expect(seg?.activeUfs).toEqual(['GO', 'MT']);
    expect(seg?.totalUfs).toBe(2);
  });

  it('UF sem região no mapping cai na própria sigla (nunca some)', () => {
    const model = buildPhenoModel([row('Rice', 'XX', ['P', '', '', '', '', '', '', '', '', '', '', ''])], regions);
    expect(model.lanes[0]?.region).toBe('XX');
  });

  it('expõe teto de faixas para o caller paginar/rotular', () => {
    expect(MAX_PHENO_LANES).toBeGreaterThan(0);
  });
});

describe('seasonLabelForDate (selo safra Out→Set)', () => {
  it('outubro abre a safra nova; setembro ainda é da safra vigente', () => {
    expect(seasonLabelForDate(new Date(2025, 9, 16))).toBe('2025/26');
    expect(seasonLabelForDate(new Date(2026, 8, 30))).toBe('2025/26');
    expect(seasonLabelForDate(new Date(2026, 0, 5))).toBe('2025/26');
    expect(seasonLabelForDate(new Date(2026, 9, 1))).toBe('2026/27');
  });
});
