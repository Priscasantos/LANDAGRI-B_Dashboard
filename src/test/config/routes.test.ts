import { describe, it, expect } from 'vitest';
import { commandIndex } from '../../config/routes';

const LEGACY_EN_TITLES = [
  'Temporal Analysis',
  'Comparative Analysis',
  'Detailed Analysis',
  'Agriculture Overview',
  'Crop Calendar',
  'Agriculture Availability',
];

describe('commandIndex (PT navigation dictionary)', () => {
  it('contains no legacy English sub-route titles', () => {
    const titles = commandIndex.map((entry) => entry.title);
    for (const legacy of LEGACY_EN_TITLES) {
      expect(titles).not.toContain(legacy);
    }
  });

  it('exposes the PT sub-route titles with unchanged urls', () => {
    const byUrl = new Map(commandIndex.map((entry) => [entry.url, entry.title]));
    expect(byUrl.get('/initiative-analysis/temporal')).toBe('Análise Temporal');
    expect(byUrl.get('/initiative-analysis/comparative')).toBe('Análise Comparativa');
    expect(byUrl.get('/initiative-analysis/detailed')).toBe('Análise Detalhada');
    expect(byUrl.get('/agricultural-analysis/overview')).toBe('Panorama Agrícola');
    expect(byUrl.get('/agricultural-analysis/crop-calendar')).toBe('Calendário de Culturas');
    expect(byUrl.get('/agricultural-analysis/availability')).toBe('Disponibilidade Agrícola');
  });
});
