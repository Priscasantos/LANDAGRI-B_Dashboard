import { describe, it, expect } from 'vitest';
import { buildPamUnified } from '../../../scripts/preprocess-data.mjs';
import unifiedJson from '../../data/processed/pam_unified.json';
import type { PamUnified } from '../../lib/agriP2b';

const ptFixture = {
  metadata: {
    source: 'IBGE - PT',
    source_url: 'https://example.test/pam',
    survey: 'Produção Agrícola Municipal',
    survey_code: '1612',
    territory_level: 'Nacional (Brasil)',
    periodicity: 'Anual',
    period_range: '2018-2025',
    last_updated: '2026-10-16',
    description: 'PT',
    variables: { 214: 'Quantidade produzida (Toneladas)' },
    pam_2025_status: 'definitiva',
  },
  data: {
    producao_agricola: {
      soja: {
        codigo: '2713',
        nome: 'Soja (em grão)',
        quantidade_produzida_toneladas: { 2025: 1000 },
        area_colhida_hectares: { 2025: 500 },
        rendimento_medio_kg_por_ha: { 2025: 2000 },
      },
    },
    resumo_anual: {
      2025: {
        total_area_colhida_hectares: 500,
        principais_culturas: ['soja'],
        valor_total_producao_bilhoes_reais: 927,
        fonte_valor_producao: 'IBGE PAM 2025 definitiva',
      },
    },
  },
};

const enFixture = {
  metadata: {
    source: 'IBGE - EN',
    source_url: 'https://example.test/pam',
    survey: 'Municipal Agricultural Production',
    survey_code: '1612',
    territory_level: 'National (Brazil)',
    periodicity: 'Annual',
    period_range: '2018-2025',
    last_updated: '2026-10-16',
    description: 'EN',
    variables: { 214: 'Production quantity (Tonnes)' },
    pam_2025_status: 'final',
  },
  data: {
    agricultural_production: {
      soybean: {
        code: '2713',
        name: 'Soybean (grain)',
        production_quantity_tonnes: { 2025: 1000 },
        harvested_area_hectares: { 2025: 500 },
        average_yield_kg_per_ha: { 2025: 2000 },
      },
    },
    summary_annual: {
      2025: {
        total_harvested_area_hectares: 500,
        main_crops: ['soybean'],
        total_production_value_billion_reais: 927,
        production_value_source: 'IBGE PAM 2025 final',
      },
    },
  },
};

describe('buildPamUnified (Fase 1, item 4)', () => {
  it('une PT+EN sob chaves estáveis com dicionário {pt, en} e série única', () => {
    const out = buildPamUnified(ptFixture, enFixture) as {
      metadata: Record<string, unknown>;
      crops: Record<string, Record<string, unknown>>;
      summary_annual: Record<string, Record<string, unknown>>;
    };
    expect(Object.keys(out.crops)).toEqual(['soybean']);
    expect(out.crops.soybean).toMatchObject({
      code: '2713',
      name: 'Soybean (grain)',
      nome: 'Soja (em grão)',
      production_quantity_tonnes: { 2025: 1000 },
    });
    expect(out.metadata.pam_2025_status).toMatchObject({ pt: 'definitiva', en: 'final' });
    expect(out.summary_annual['2025'].total_production_value_billion_reais).toBe(927);
  });

  it('falha alto em divergência numérica (nunca meio-mescla silenciosa)', () => {
    const drifted = structuredClone(enFixture) as typeof enFixture;
    drifted.data.agricultural_production.soybean.production_quantity_tonnes['2025'] = 999;
    expect(() => buildPamUnified(ptFixture, drifted)).toThrow(/numeric mismatch/);
  });

  it('falha alto em conjuntos de códigos divergentes', () => {
    const missing = structuredClone(enFixture) as typeof enFixture;
    // @ts-expect-error fixture propositalmente incompleto
    missing.data.agricultural_production = {};
    expect(() => buildPamUnified(ptFixture, missing)).toThrow(/code sets diverged/);
  });

  it('payload processado: 11 culturas, metadados bilíngues, sem chaves PT legadas', () => {
    const pam = unifiedJson as PamUnified;
    expect(Object.keys(pam.crops ?? {})).toHaveLength(11);
    const raw = JSON.stringify(unifiedJson);
    expect(raw).not.toContain('producao_agricola');
    expect(raw).not.toContain('quantidade_produzida_toneladas');
    expect(raw).not.toContain('resumo_anual');
  });
});
