import { describe, expect, it } from 'vitest';
import {
  getInitiativeDisplayName,
  normalizeCropOrdinals,
  translateActivity,
  translateCropName,
  translateMonth,
  translateMonthShort,
  translateRegion,
  translateSeason,
  translateTerm,
} from './glossary';

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

describe('glossary Fase 2 — valores de DADOS exibidos (só display, bruto intacto)', () => {
  it.each([
    ['Soybean', 'Soja'],
    ['Corn', 'Milho'],
    ['Corn (1st harvest)', 'Milho (1ª safra)'],
    ['Corn (2nd harvest)', 'Milho (2ª safra)'],
    ['Corn (3rd harvest)', 'Milho (3ª safra)'],
    ['Corn (1st + 2nd harvest)', 'Milho (1ª + 2ª safra)'],
    ['Corn (Total)', 'Milho (Total)'],
    ['Cotton', 'Algodão'],
    ['Rice', 'Arroz'],
    ['Irrigated Rice', 'Arroz Irrigado'],
    ['Beans', 'Feijão'],
    ['Beans (1st harvest)', 'Feijão (1ª safra)'],
    ['Beans (2nd harvest)', 'Feijão (2ª safra)'],
    ['Beans (3rd harvest)', 'Feijão (3ª safra)'],
    ['Beans (1st + 2nd + 3rd harvest)', 'Feijão (1ª + 2ª + 3ª safra)'],
    ['Wheat', 'Trigo'],
    ['Sorghum', 'Sorgo'],
    ['Sunflower', 'Girassol'],
    ['Peanut', 'Amendoim'],
    ['Peanut (1st harvest)', 'Amendoim (1ª safra)'],
    ['Coffee', 'Café'],
    ['Sugar cane', 'Cana-de-açúcar'],
    ['Sugar cane mill', 'Usina de cana-de-açúcar'],
    ['Other summer crops', 'Outras culturas de verão'],
    ['Other winter crops', 'Outras culturas de inverno'],
    ['Sugarcane', 'Cana-de-açúcar'],
    ['Cassava', 'Mandioca'],
    ['Sweet potato', 'Batata-doce'],
    ['Potato', 'Batata-inglesa'],
    ['Oat', 'Aveia'],
    ['Oat (grain)', 'Aveia (em grão)'],
    ['Peanut (in shell)', 'Amendoim (em casca)'],
    ['Rice (in husk)', 'Arroz (em casca)'],
    ['Corn (grain)', 'Milho (em grão)'],
    ['Soybean (grain)', 'Soja (em grão)'],
    ['Wheat (grain)', 'Trigo (em grão)'],
    ['Cotton (lint and seed)', 'Algodão herbáceo (em caroço)'],
  ])('translates crop %s → %s in pt-BR and keeps EN original', (en, pt) => {
    expect(translateCropName(en, 'pt-BR')).toBe(pt);
    expect(translateCropName(en, 'en')).toBe(en);
    expect(translateTerm('crop', en, 'pt-BR')).toBe(pt);
  });

  it('fixes CONAB ordinal typo before translating crops', () => {
    expect(normalizeCropOrdinals('Beans (3th harvest)')).toBe('Beans (3rd harvest)');
    expect(translateCropName('Beans (3th harvest)', 'pt-BR')).toBe('Feijão (3ª safra)');
    expect(translateCropName('Corn (3th harvest)', 'en')).toBe('Corn (3rd harvest)');
  });

  it('passes unknown crops through untouched', () => {
    expect(translateCropName('Quinoa', 'pt-BR')).toBe('Quinoa');
    expect(translateCropName('Quinoa', 'en')).toBe('Quinoa');
  });

  it.each([
    ['North', 'Norte'],
    ['Northeast', 'Nordeste'],
    ['Central-West', 'Centro-Oeste'],
    ['Midwest', 'Centro-Oeste'],
    ['Southeast', 'Sudeste'],
    ['South', 'Sul'],
    ['Country', 'Brasil'],
  ])('translates region %s → %s in pt-BR and keeps EN original', (en, pt) => {
    expect(translateRegion(en, 'pt-BR')).toBe(pt);
    expect(translateRegion(en, 'en')).toBe(en);
  });

  it.each([
    ['January', 'Janeiro'],
    ['February', 'Fevereiro'],
    ['March', 'Março'],
    ['April', 'Abril'],
    ['May', 'Maio'],
    ['June', 'Junho'],
    ['July', 'Julho'],
    ['August', 'Agosto'],
    ['September', 'Setembro'],
    ['October', 'Outubro'],
    ['November', 'Novembro'],
    ['December', 'Dezembro'],
  ])('translates month %s → %s in pt-BR and keeps EN original', (en, pt) => {
    expect(translateMonth(en, 'pt-BR')).toBe(pt);
    expect(translateMonth(en, 'en')).toBe(en);
  });

  it.each([
    ['Jan', 'Jan'],
    ['Feb', 'Fev'],
    ['Mar', 'Mar'],
    ['Apr', 'Abr'],
    ['May', 'Mai'],
    ['Jun', 'Jun'],
    ['Jul', 'Jul'],
    ['Aug', 'Ago'],
    ['Sep', 'Set'],
    ['Oct', 'Out'],
    ['Nov', 'Nov'],
    ['Dec', 'Dez'],
  ])('translates short month %s → %s in pt-BR and keeps EN original', (en, pt) => {
    expect(translateMonthShort(en, 'pt-BR')).toBe(pt);
    expect(translateMonthShort(en, 'en')).toBe(en);
  });

  it.each([
    ['Spring', 'Primavera'],
    ['Summer', 'Verão'],
    ['Autumn', 'Outono'],
    ['Winter', 'Inverno'],
    ['Spring (Oct-Dec)', 'Primavera (Out-Dez)'],
    ['Summer (Jan-Mar)', 'Verão (Jan-Mar)'],
    ['Autumn (Apr-Jun)', 'Outono (Abr-Jun)'],
    ['Winter (Jul-Sep)', 'Inverno (Jul-Set)'],
  ])('translates season %s → %s in pt-BR and keeps EN original', (en, pt) => {
    expect(translateSeason(en, 'pt-BR')).toBe(pt);
    expect(translateSeason(en, 'en')).toBe(en);
  });

  it.each([
    ['Planting', 'Plantio'],
    ['Harvest', 'Colheita'],
    ['Planting and Harvest', 'Plantio e Colheita'],
    ['Total Activity', 'Atividade Total'],
    ['Activity Intensity', 'Intensidade de Atividade'],
    ['Peak Intensity', 'Pico de Intensidade'],
    ['Total Production (thousand tons)', 'Produção Total (mil toneladas)'],
    ['Total Production (tonnes)', 'Produção Total (toneladas)'],
    ['Harvested Area (hectares)', 'Área Colhida (hectares)'],
  ])('translates activity %s → %s in pt-BR and keeps EN original', (en, pt) => {
    expect(translateActivity(en, 'pt-BR')).toBe(pt);
    expect(translateActivity(en, 'en')).toBe(en);
  });

  it('passes unknown data values through untouched in both locales', () => {
    expect(translateTerm('region', 'Atlantis', 'pt-BR')).toBe('Atlantis');
    expect(translateTerm('month', 'Smarch', 'en')).toBe('Smarch');
    expect(translateTerm('season', 'Monsoon', 'pt-BR')).toBe('Monsoon');
    expect(translateTerm('activity', 'Fallowing', 'pt-BR')).toBe('Fallowing');
  });
});
