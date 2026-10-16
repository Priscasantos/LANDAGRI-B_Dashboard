import { describe, it, expect } from 'vitest';
import { parseInitiatives } from '../../lib/dataParser';
import ibgeEn from '../../data/processed/brazilian_ibge_agricultural_data.json';
import ibgePt from '../../data/processed/brazilian_agricultural_data.json';
import initiativesJson from '../../data/processed/initiatives.json';

type CropEn = {
  production_quantity_tonnes: Record<string, number>;
  harvested_area_hectares: Record<string, number>;
  average_yield_kg_per_ha?: Record<string, number>;
};
type CropPt = {
  quantidade_produzida_toneladas: Record<string, number>;
  area_colhida_hectares: Record<string, number>;
  rendimento_medio_kg_por_ha?: Record<string, number>;
};

const YEARS = ['2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025'];

describe('P1 PAM 2025 definitiva (PT+EN espelhados)', () => {
  const en = ibgeEn as {
    metadata: { last_updated: string; pam_2025_status?: string };
    data: {
      agricultural_production: Record<string, CropEn>;
      summary_annual: Record<string, Record<string, unknown>>;
    };
  };
  const pt = ibgePt as {
    metadata: { last_updated: string; pam_2025_status?: string };
    data: {
      producao_agricola: Record<string, CropPt>;
      resumo_anual: Record<string, Record<string, unknown>>;
    };
  };

  it('mantém 11 culturas espelhadas PT/EN sem deduplicar', () => {
    expect(Object.keys(en.data.agricultural_production)).toHaveLength(11);
    expect(Object.keys(pt.data.producao_agricola)).toHaveLength(11);
  });

  it('traz average_yield/rendimento_medio 2018-2025 derivado de quantidade/área', () => {
    for (const crop of Object.values(en.data.agricultural_production)) {
      expect(Object.keys(crop.average_yield_kg_per_ha ?? {})).toEqual(YEARS);
      for (const y of YEARS) {
        const expected = Math.round(
          (crop.production_quantity_tonnes[y] * 1000) / crop.harvested_area_hectares[y],
        );
        expect(crop.average_yield_kg_per_ha?.[y]).toBe(expected);
      }
    }
    for (const crop of Object.values(pt.data.producao_agricola)) {
      expect(Object.keys(crop.rendimento_medio_kg_por_ha ?? {})).toEqual(YEARS);
    }
    // Espelho: soja 2025 rende igual nos dois arquivos
    expect(en.data.agricultural_production.soybean.average_yield_kg_per_ha?.['2025']).toBe(
      pt.data.producao_agricola.soja.rendimento_medio_kg_por_ha?.['2025'],
    );
  });

  it('registra o valor da produção 2025 (R$ 927 bi) no resumo anual + bump last_updated', () => {
    expect(en.data.summary_annual['2025'].total_production_value_billion_reais).toBe(927);
    expect(pt.data.resumo_anual['2025'].valor_total_producao_bilhoes_reais).toBe(927);
    expect(en.metadata.pam_2025_status).toBe('final');
    expect(pt.metadata.pam_2025_status).toBe('definitiva');
    expect(en.metadata.last_updated).toBe('2026-10-16');
    expect(pt.metadata.last_updated).toBe('2026-10-16');
  });
});

describe('P1 initiatives.json (15+ entradas coerentes, anos estendidos)', () => {
  const meta = initiativesJson as Record<
    string,
    {
      acronym?: string;
      available_years?: number[];
      update_frequency?: string;
      near_real_time?: boolean;
      status?: string;
      latest_deforestation_rate?: { year: number; area_km2: number };
      accuracy?: { by_collection?: { collection_name: string; accuracy: number | null }[] };
    }
  >;

  it('tem 15+ entradas, todas com sigla e série de anos não-vazia', () => {
    const names = Object.keys(meta);
    expect(names.length).toBeGreaterThanOrEqual(15);
    for (const [name, entry] of Object.entries(meta)) {
      expect(entry.acronym, name).toBeTruthy();
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
});
