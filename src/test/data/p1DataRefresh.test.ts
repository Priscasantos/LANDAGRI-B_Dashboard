import { describe, it, expect } from 'vitest';
import { parseInitiatives } from '../../lib/dataParser';
import type { PamUnified } from '../../lib/agriP2b';
import pamUnifiedJson from '../../data/processed/pam_unified.json';
import initiativesJson from '../../data/processed/initiatives.json';

const YEARS = ['2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025'];

const EXPECTED_CROPS = [
  'peanut',
  'rice',
  'oat',
  'sweet_potato',
  'potato',
  'sugarcane',
  'cassava',
  'corn',
  'soybean',
  'wheat',
  'cotton',
] as const;

describe('P1 PAM 2025 definitiva (payload unificado, sem duplicar série)', () => {
  const pam = pamUnifiedJson as PamUnified;
  const crops = pam.crops ?? {};

  it('traz 11 culturas sob chaves estáveis com nomes PT+EN', () => {
    expect(Object.keys(crops).sort()).toEqual([...EXPECTED_CROPS].sort());
    for (const [key, crop] of Object.entries(crops)) {
      expect(crop.code, key).toBeTruthy();
      expect(crop.name, key).toBeTruthy();
      expect(crop.nome, key).toBeTruthy();
    }
    expect(crops.soybean.name).toBe('Soybean (grain)');
    expect(crops.soybean.nome).toBe('Soja (em grão)');
  });

  it('guarda UMA série numérica 2018-2025 + rendimento derivado de quantidade/área', () => {
    for (const [key, crop] of Object.entries(crops)) {
      expect(Object.keys(crop.average_yield_kg_per_ha ?? {}), key).toEqual(YEARS);
      for (const y of YEARS) {
        const expected = Math.round(
          (crop.production_quantity_tonnes?.[y] ?? 0) * 1000 /
            (crop.harvested_area_hectares?.[y] ?? 1),
        );
        expect(crop.average_yield_kg_per_ha?.[y], `${key}/${y}`).toBe(expected);
      }
    }
    expect(crops.soybean.average_yield_kg_per_ha?.['2025']).toBe(3470);
  });

  it('registra o valor da produção 2025 (R$ 927 bi) no resumo anual + metadados bilíngues', () => {
    expect(pam.summary_annual?.['2025']?.total_production_value_billion_reais).toBe(927);
    expect(pam.metadata?.pam_2025_status).toMatchObject({ pt: 'definitiva', en: 'final' });
    expect(pam.metadata?.last_updated).toBe('2026-10-16');
    expect(pam.metadata?.survey).toMatchObject({
      pt: 'Produção Agrícola Municipal',
      en: 'Municipal Agricultural Production',
    });
  });
});

describe('P1 initiatives.json (15+ entradas coerentes, anos estendidos)', () => {
  const meta = initiativesJson as Record<
    string,
    {
      acronym?: string;
      status?: string;
      available_years?: number[];
      update_frequency?: string;
      near_real_time?: boolean;
      status_note?: string;
      latest_deforestation_rate?: { year: number; area_km2: number };
      accuracy?: { by_collection?: { collection_name: string; accuracy: number | null }[] };
    }
  >;

  it('tem 15+ entradas, todas com sigla, status e série de anos não-vazia', () => {
    const names = Object.keys(meta);
    expect(names.length).toBeGreaterThanOrEqual(15);
    for (const [name, entry] of Object.entries(meta)) {
      expect(entry.acronym, name).toBeTruthy();
      expect(entry.status, name).toMatch(/^(active|legacy)$/);
      expect(Array.isArray(entry.available_years), name).toBe(true);
      expect(entry.available_years!.length, name).toBeGreaterThan(0);
    }
  });

  it('estende os anos-alvo: PRODES/DETER→2025, Dynamic World→2025 NRT, ESRI/MapBiomas→2024', () => {
    const yearEnd = (k: string) => Math.max(...meta[k].available_years!);
    expect(yearEnd('PRODES Deforestation, Warnings and Vegetation for Brazilian Biomes')).toBe(2025);
    expect(yearEnd('DETER Deforestation, Warnings and Vegetation for Brazilian Biomes')).toBe(2025);
    expect(yearEnd('Google Dynamic World V1')).toBe(2025);
    expect(yearEnd('ESRI-10m Annual LULC')).toBe(2024);
    expect(yearEnd('MapBiomas')).toBe(2024);
  });

  it('marca NRT (Dynamic World, DETER), taxa PRODES 2025 e CGLS legacy', () => {
    expect(meta['Google Dynamic World V1'].near_real_time).toBe(true);
    expect(meta['DETER Deforestation, Warnings and Vegetation for Brazilian Biomes'].near_real_time).toBe(true);
    expect(
      meta['PRODES Deforestation, Warnings and Vegetation for Brazilian Biomes']
        .latest_deforestation_rate,
    ).toMatchObject({ year: 2025, area_km2: 5731 });
    expect(meta['Copernicus Global Land Cover Service Dynamic Land Cover'].status).toBe('legacy');
    const col10 = meta['MapBiomas'].accuracy?.by_collection?.find((c) =>
      c.collection_name.includes('Collection 10'),
    );
    expect(col10?.accuracy).toBeNull();
  });

  it('parseInitiatives consome todas as entradas sem quebrar (Year_End máx 2025)', () => {
    const rows = parseInitiatives(meta as never);
    expect(rows.length).toBeGreaterThanOrEqual(15);
    expect(Math.max(...rows.map((r) => r.Year_End))).toBe(2025);
    for (const r of rows) expect(r.Acronym).not.toBe('N/A');
  });

  it('accuracies sem avaliação viram n/a justificado (nunca 0.0 inventado)', () => {
    const rows = parseInitiatives(meta as never);
    for (const r of rows) {
      expect(r.Accuracy_Label, r.Name).toBeTruthy();
    }
    const byName = Object.fromEntries(rows.map((r) => [r.Name, r]));
    // IBGE (sem avaliação) e CONAB-AM (incompleta): n/a + motivo da fonte.
    for (const name of [
      'IBGE Monitoring Land Cover and Land Use',
      'National Supply Company Agricultural Mapping',
    ]) {
      expect(byName[name].Accuracy).toBe(0);
      expect(byName[name].Accuracy_Label).toBe('n/a');
      expect(byName[name].Accuracy_Note, name).toBeTruthy();
    }
    // Avaliadas mantêm rótulo numérico, sem nota.
    expect(byName['Global Pasture Watch (GPW)'].Accuracy_Label).toBe('91.0');
    expect(byName['Global Pasture Watch (GPW)'].Accuracy_Note).toBe('');
  });
});
