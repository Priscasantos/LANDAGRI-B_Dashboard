import { describe, expect, it } from 'vitest';
import { getInitiativeDisplayName, translateTerm } from './glossary';

describe('glossary (Fase 1 — só UI traduzida, sem re-fetch)', () => {
  it('translates coverage enums per locale', () => {
    expect(translateTerm('coverage', 'National', 'pt-BR')).toBe('Nacional');
    expect(translateTerm('coverage', 'National', 'en')).toBe('National');
    expect(translateTerm('coverage', 'Global', 'pt-BR')).toBe('Global');
  });

  it('translates methodology enums per locale', () => {
    expect(translateTerm('methodology', 'Hybrid', 'pt-BR')).toBe('Híbrida');
    expect(translateTerm('methodology', 'Hybrid', 'en')).toBe('Hybrid');
    expect(translateTerm('methodology', 'Visual Interpretation', 'pt-BR')).toBe(
      'Interpretação Visual',
    );
  });

  it('translates frequency and headers', () => {
    expect(translateTerm('frequency', 'Annual', 'pt-BR')).toBe('Anual');
    expect(translateTerm('header', 'initiative', 'en')).toBe('Initiative');
    expect(translateTerm('header', 'coverage', 'pt-BR')).toBe('Cobertura');
  });

  it('passes units and unknown values through untouched', () => {
    expect(translateTerm('unit', 'ha', 'pt-BR')).toBe('ha');
    expect(translateTerm('unit', 'km²', 'en')).toBe('km²');
    expect(translateTerm('coverage', 'Something New', 'pt-BR')).toBe('Something New');
  });

  it('keeps initiative proper names identical in both locales', () => {
    expect(getInitiativeDisplayName('MapBiomas', 'pt-BR')).toBe('MapBiomas');
    expect(getInitiativeDisplayName('MapBiomas', 'en')).toBe('MapBiomas');
  });
});
