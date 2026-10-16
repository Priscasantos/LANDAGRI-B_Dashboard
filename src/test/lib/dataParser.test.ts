import { describe, it, expect } from 'vitest';
import { parseInitiatives, normalizeValues, parseAvailableYears, cleanColumnName } from '../../lib/dataParser';
import type { InitiativeMetadata } from '../../types/initiative';

describe('dataParser', () => {
  it('should parse empty metadata gracefully', () => {
    const result = parseInitiatives({});
    expect(result).toEqual([]);
  });

  it('should parse a single initiative', () => {
    const metadata: Record<string, InitiativeMetadata> = {
      'Test Initiative': {
        acronym: 'TEST',
        provider: 'Test Provider',
        source: 'Test Source',
        spatial_resolution: 30,
        available_years: [2020, 2021, 2022],
        temporal_frequency: 'Annual',
        update_frequency: 'Yearly',
        reference_system: 'EPSG:4326',
        methodology: 'Shallow ML',
        classification_method: 'Random Forest',
        coverage: 'National',
        overall_accuracy: 92.5,
        number_of_classes: 15,
        class_legend: 'Forest, Water, Urban',
        number_of_agriculture_classes: 3,
        agricultural_capabilities: 'Crop monitoring',
        algorithm: 'RF',
        sensors_referenced: [{ sensor_key: 'S2' }],
      },
    };

    const result = parseInitiatives(metadata);
    expect(result).toHaveLength(1);
    expect(result[0].Name).toBe('Test Initiative');
    expect(result[0].Acronym).toBe('TEST');
    expect(result[0].Coverage).toBe('National');
    expect(result[0].Methodology).toBe('Shallow ML');
    expect(result[0].Resolution).toBe(30);
    expect(result[0].Accuracy).toBe(92.5);
    expect(result[0].Number_of_Classes).toBe(15);
    expect(result[0].Available_Years).toEqual([2020, 2021, 2022]);
  });

  it('maps legacy methodology names to taxonomy leaves without re-bucketing unknowns', () => {
    const makeMeta = (methodology: string): Record<string, InitiativeMetadata> => ({
      Test: {
        acronym: 'T', provider: 'P', source: 'S',
        spatial_resolution: 10, available_years: [2020],
        temporal_frequency: '', update_frequency: '', reference_system: '',
        methodology, classification_method: '', coverage: 'Global',
        number_of_classes: 5, class_legend: '', number_of_agriculture_classes: 0,
        agricultural_capabilities: '', algorithm: '', sensors_referenced: [],
      },
    });
    // Bucket largo pré-taxonomia → ramo não-profundo.
    expect(parseInitiatives(makeMeta('Machine Learning'))[0].Methodology).toBe('Shallow ML');
    expect(parseInitiatives(makeMeta('Supervised Machine Learning'))[0].Methodology).toBe('Shallow ML');
    // Texto livre multi-família → Hybrid (regra ≥2 famílias do SSoT).
    expect(
      parseInitiatives(makeMeta('Machine Learning, Statistical Methods, Visual Interpretation'))[0]
        .Methodology,
    ).toBe('Hybrid');
    // Folhas canônicas passam intactas.
    expect(parseInitiatives(makeMeta('Deep Learning'))[0].Methodology).toBe('Deep Learning');
    expect(parseInitiatives(makeMeta('Statistical / Spectral'))[0].Methodology).toBe(
      'Statistical / Spectral',
    );
    // Desconhecido: passthrough, nunca re-bucket silencioso.
    expect(parseInitiatives(makeMeta('Something New'))[0].Methodology).toBe('Something New');
  });

  it('should handle null accuracy', () => {
    const metadata: Record<string, InitiativeMetadata> = {
      'Test': {
        acronym: 'T', provider: 'P', source: 'S',
        spatial_resolution: 10, available_years: [2020],
        temporal_frequency: '', update_frequency: '', reference_system: '',
        methodology: 'DL', classification_method: '', coverage: 'Global',
        number_of_classes: 5, class_legend: '', number_of_agriculture_classes: 0,
        agricultural_capabilities: '', algorithm: '', sensors_referenced: [],
      },
    };
    const result = parseInitiatives(metadata);
    expect(result[0].Accuracy).toBe(0);
  });

  it('should handle accuracy object with by_product', () => {
    const metadata: Record<string, InitiativeMetadata> = {
      'Test': {
        acronym: 'T', provider: 'P', source: 'S',
        spatial_resolution: 10, available_years: [2020],
        temporal_frequency: '', update_frequency: '', reference_system: '',
        methodology: 'DL', classification_method: '', coverage: 'Global',
        overall_accuracy: { by_product: [{ product: 'P1', accuracy: 85 }, { product: 'P2', accuracy: 95 }] },
        number_of_classes: 5, class_legend: '', number_of_agriculture_classes: 0,
        agricultural_capabilities: '', algorithm: '', sensors_referenced: [],
      },
    };
    const result = parseInitiatives(metadata);
    expect(result[0].Accuracy).toBe(90);
  });
});

describe('normalizeValues', () => {
  it('should normalize to [0, 1] range', () => {
    expect(normalizeValues([0, 50, 100])).toEqual([0, 0.5, 1]);
  });

  it('should handle equal values', () => {
    expect(normalizeValues([5, 5, 5])).toEqual([0.5, 0.5, 0.5]);
  });

  it('should handle empty array', () => {
    expect(normalizeValues([])).toEqual([]);
  });
});

describe('parseAvailableYears', () => {
  it('should parse JSON string', () => {
    expect(parseAvailableYears('[2020, 2021, 2022]')).toEqual([2020, 2021, 2022]);
  });

  it('should return array as-is', () => {
    expect(parseAvailableYears([2020, 2021])).toEqual([2020, 2021]);
  });

  it('should return empty for invalid string', () => {
    expect(parseAvailableYears('invalid')).toEqual([]);
  });
});

describe('cleanColumnName', () => {
  it('should replace underscores with spaces', () => {
    expect(cleanColumnName('hello_world')).toBe('Hello World');
  });

  it('should capitalize words', () => {
    expect(cleanColumnName('test_column_name')).toBe('Test Column Name');
  });
});
