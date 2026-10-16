import { describe, it, expect } from 'vitest';
import {
  PAM_GRAIN_KEYS,
  PAM_YEARS,
  buildPamYieldSeries,
  buildSeasonClose,
  deltaPct,
  formatDeltaPct,
  type ConabCrops,
  type PamProduction,
} from '../../lib/agriP2b';
import pamData from '../../data/processed/brazilian_agricultural_data.json';
import conabData from '../../data/processed/conab_agricultural_data.json';

describe('agriP2b helpers (P2b charts)', () => {
  it('expõe anos PAM 2018–2025 e chaves de grãos presentes no JSON', () => {
    expect(PAM_YEARS).toEqual(['2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025']);
    const prod = (pamData as { data: { producao_agricola: PamProduction } }).data.producao_agricola;
    for (const key of PAM_GRAIN_KEYS) {
      expect(prod[key], `chave PAM ausente: ${key}`).toBeDefined();
      expect(prod[key].rendimento_medio_kg_por_ha['2025']).toBeGreaterThan(0);
    }
  });

  it('buildPamYieldSeries monta multi-série kg/ha sem inventar anos', () => {
    const prod = (pamData as { data: { producao_agricola: PamProduction } }).data.producao_agricola;
    const series = buildPamYieldSeries(prod, PAM_GRAIN_KEYS, PAM_YEARS);
    expect(series.length).toBe(PAM_GRAIN_KEYS.length);
    const soja = series.find((s) => s.name === 'Soja (em grão)');
    expect(soja).toBeDefined();
    expect(soja?.x).toEqual(PAM_YEARS);
    // Valor real do JSON: soja 2025 = 3470 kg/ha
    expect(soja?.y[PAM_YEARS.indexOf('2025')]).toBe(3470);
  });

  it('deltaPct calcula variação percentual e null sem base', () => {
    expect(deltaPct(110, 100)).toBeCloseTo(10, 5);
    expect(deltaPct(90, 100)).toBeCloseTo(-10, 5);
    expect(deltaPct(50, 0)).toBeNull();
    expect(formatDeltaPct(10.256, 'pt-BR')).toBe('+10,3%');
    expect(formatDeltaPct(-2, 'en')).toBe('-2.0%');
    expect(formatDeltaPct(null, 'pt-BR')).toBe('–');
  });

  it('buildSeasonClose usa só safras presentes no JSON CONAB (24/25 × 25/26)', () => {
    const crops = (conabData as { crops: ConabCrops }).crops;
    const rows = buildSeasonClose(crops, '2024/25', '2025/26', 6);
    expect(rows.length).toBe(6);
    // Ordenado por produção 24/25 desc — soja em primeiro
    expect(rows[0].key).toBe('soybean');
    expect(rows[0].prodPrev).toBeGreaterThan(0);
    expect(rows[0].prodNext).toBeGreaterThan(0);
    expect(typeof rows[0].deltaProd).toBe('number');
    expect(typeof rows[0].deltaArea).toBe('number');
  });
});
