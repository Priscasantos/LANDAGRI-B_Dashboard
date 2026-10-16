import { describe, it, expect } from 'vitest';
import {
  PAM_GRAIN_KEYS,
  PAM_YEARS,
  buildPamYieldSeries,
  buildSeasonClose,
  deltaPct,
  formatDeltaPct,
  pamCropName,
  type ConabCrops,
  type PamProduction,
  type PamUnified,
} from '../../lib/agriP2b';
import pamUnified from '../../data/processed/pam_unified.json';
import conabData from '../../data/processed/conab_agricultural_data.json';

describe('agriP2b helpers (P2b charts)', () => {
  it('expõe anos PAM 2018–2025 e chaves de grãos presentes no payload unificado', () => {
    expect(PAM_YEARS).toEqual(['2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025']);
    const prod = (pamUnified as PamUnified).crops as PamProduction;
    for (const key of PAM_GRAIN_KEYS) {
      expect(prod[key], `chave PAM ausente: ${key}`).toBeDefined();
      expect(prod[key].average_yield_kg_per_ha?.['2025']).toBeGreaterThan(0);
    }
  });

  it('buildPamYieldSeries monta multi-série kg/ha sem inventar anos', () => {
    const prod = (pamUnified as PamUnified).crops as PamProduction;
    const series = buildPamYieldSeries(prod, PAM_GRAIN_KEYS, PAM_YEARS);
    expect(series.length).toBe(PAM_GRAIN_KEYS.length);
    const soja = series.find((s) => s.name === 'Soja (em grão)');
    expect(soja).toBeDefined();
    expect(soja?.x).toEqual(PAM_YEARS);
    // Valor real do JSON: soja 2025 = 3470 kg/ha
    expect(soja?.y[PAM_YEARS.indexOf('2025')]).toBe(3470);
  });

  it('localiza nomes via dicionário {en, pt} sem re-fetch', () => {
    const prod = (pamUnified as PamUnified).crops as PamProduction;
    expect(pamCropName(prod.soybean, 'pt-BR')).toBe('Soja (em grão)');
    expect(pamCropName(prod.soybean, 'en')).toBe('Soybean (grain)');
    const seriesEn = buildPamYieldSeries(prod, ['soybean'], PAM_YEARS, 'en');
    expect(seriesEn[0]?.name).toBe('Soybean (grain)');
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
