import { describe, expect, it } from 'vitest';
import {
  getInitiativeDisplayName,
  getInitiativeShortName,
  getProviderShortName,
  normalizeCropOrdinals,
  SHORT_LABEL_MAX_CARD,
  SHORT_LABEL_MAX_HEADER,
  translateActivity,
  translateCropName,
  translateMonth,
  translateMonthShort,
  translateRegion,
  translateSeason,
  truncateLabel,
  translateTerm,
} from './glossary';

describe('glossary (Fase 1 — só UI traduzida, sem re-fetch)', () => {
  it('translates coverage enums per locale', () => {
    expect(translateTerm('coverage', 'National', 'pt-BR')).toBe('Nacional');
    expect(translateTerm('coverage', 'National', 'en')).toBe('National');
    expect(translateTerm('coverage', 'Global', 'pt-BR')).toBe('Global');
  });

  it('translates methodology enums per locale (MECE taxonomy)', () => {
    expect(translateTerm('methodology', 'Hybrid', 'pt-BR')).toBe('Híbrida');
    expect(translateTerm('methodology', 'Hybrid', 'en')).toBe('Hybrid');
    expect(translateTerm('methodology', 'Visual Interpretation', 'pt-BR')).toBe(
      'Interpretação Visual',
    );
    expect(translateTerm('methodology', 'Shallow ML', 'pt-BR')).toBe('ML Raso');
    expect(translateTerm('methodology', 'Shallow ML', 'en')).toBe('Shallow ML');
    expect(translateTerm('methodology', 'Deep Learning', 'pt-BR')).toBe(
      'Aprendizado Profundo',
    );
    expect(translateTerm('methodology', 'Statistical / Spectral', 'pt-BR')).toBe(
      'Estatístico / Espectral',
    );
    expect(translateTerm('methodology', 'Statistical / Spectral', 'en')).toBe(
      'Statistical / Spectral',
    );
    // Legado pré-taxonomia exibe como o ramo não-profundo (só display).
    expect(translateTerm('methodology', 'Machine Learning', 'pt-BR')).toBe('ML Raso');
    expect(translateTerm('methodology', 'Machine Learning', 'en')).toBe('Shallow ML');
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

describe('glossary Fase 3 — iniciativas: Brasil/Brazil, typos de metodologia, shortName', () => {
  it('usa "Brasil" em PT e mantém "Brazil"/"Brazilian" em EN', async () => {
    const { translateInitiativeName } = await import('./glossary');
    expect(
      translateInitiativeName(
        'PRODES Deforestation, Warnings and Vegetation for Brazilian Biomes',
        'pt-BR',
      ),
    ).toBe('PRODES Deforestation, Warnings and Vegetation for Biomas Brasileiros');
    expect(
      translateInitiativeName(
        'PRODES Deforestation, Warnings and Vegetation for Brazilian Biomes',
        'en',
      ),
    ).toBe('PRODES Deforestation, Warnings and Vegetation for Brazilian Biomes');
    expect(translateInitiativeName('MapBiomas', 'pt-BR')).toBe('MapBiomas');
  });

  it('corrige typos de methodology names no display (bruto intacto)', async () => {
    const { translateMethodology } = await import('./glossary');
    expect(
      translateMethodology(
        'Visual Interpretation, Supervised Bhattacharya Classification, and Deep Learning',
        'en',
      ),
    ).toBe('Visual Interpretation, Supervised Bhattacharyya Classification, and Deep Learning');
    expect(
      translateMethodology(
        'Supervised Random Forest and U-Net Deep learning algorithms applied to Landsat series data',
        'en',
      ),
    ).toBe(
      'Supervised Random Forest and U-Net Deep Learning algorithms applied to Landsat series data',
    );
    expect(translateMethodology('Hybrid', 'pt-BR')).toBe('Híbrida');
    expect(translateMethodology('Something New', 'pt-BR')).toBe('Something New');
  });

  it('expõe shortName (sigla + nome curto traduzido) para todas as iniciativas', async () => {
    const { getInitiativeShortName } = await import('./glossary');
    expect(getInitiativeShortName('MapBiomas', 'pt-BR')).toBe('MapBiomas · Mapeamento anual do Brasil');
    expect(getInitiativeShortName('MapBiomas', 'en')).toBe('MapBiomas · Annual mapping of Brazil');
    expect(getInitiativeShortName('TerraClass Amazonia', 'pt-BR')).toBe(
      'TerraClass Amazon · Uso do solo na Amazônia',
    );
    // Forma composta "Nome (SIGLA)" do Display_Name também encurta
    expect(getInitiativeShortName('TerraClass Amazonia (TerraClass Amazon)', 'en')).toBe(
      'TerraClass Amazon · Amazon land use',
    );
    expect(getInitiativeShortName('MapBiomas (MapBiomas)', 'pt-BR')).toBe(
      'MapBiomas · Mapeamento anual do Brasil',
    );
    // Desconhecida volta intacta (nunca some)
    expect(getInitiativeShortName('Quinoa Initiative', 'pt-BR')).toBe('Quinoa Initiative');
  });
});

describe('glossary P3 — tipografia/identidade (initiativeShort/providerShort, tetos)', () => {
  it('mapeia coverage "Brazil"/"Brasil" para Nacional (PT) / National (EN)', () => {
    expect(translateTerm('coverage', 'Brazil', 'pt-BR')).toBe('Nacional');
    expect(translateTerm('coverage', 'Brazil', 'en')).toBe('National');
    expect(translateTerm('coverage', 'Brasil', 'pt-BR')).toBe('Nacional');
    expect(translateTerm('coverage', 'Brasil', 'en')).toBe('National');
  });

  it('expõe kind initiativeShort via translateTerm (mesmo rótulo do helper)', () => {
    expect(translateTerm('initiativeShort', 'MapBiomas', 'pt-BR')).toBe(
      getInitiativeShortName('MapBiomas', 'pt-BR'),
    );
    expect(translateTerm('initiativeShort', 'MapBiomas', 'en')).toBe(
      getInitiativeShortName('MapBiomas', 'en'),
    );
    expect(translateTerm('initiativeShort', 'Quinoa Initiative', 'pt-BR')).toBe(
      'Quinoa Initiative',
    );
  });

  it('expõe providerShort no padrão "[SIGLA] · Nome curto PT/EN"', () => {
    const esri = 'Environmental Systems Research Institute (ESRI), Impact Observatory, and Microsoft Maps for Good Initiative';
    expect(getProviderShortName(esri, 'pt-BR')).toBe(
      'ESRI · ESRI, Impact Observatory e Microsoft',
    );
    expect(getProviderShortName(esri, 'en')).toBe(
      'ESRI · ESRI, Impact Observatory and Microsoft',
    );
    expect(translateTerm('providerShort', esri, 'pt-BR')).toBe(
      getProviderShortName(esri, 'pt-BR'),
    );
    expect(getProviderShortName('INPE', 'pt-BR')).toBe('INPE');
  });

  it('trunca rótulos longos com elipse sem quebrar palavra curta', () => {
    expect(SHORT_LABEL_MAX_CARD).toBe(32);
    expect(SHORT_LABEL_MAX_HEADER).toBe(60);
    expect(truncateLabel('curto', SHORT_LABEL_MAX_CARD)).toBe('curto');
    const long = 'National Institute for Space Research (INPE) and Brazilian Agricultural Research Corporation (Embrapa)';
    const cut = truncateLabel(long, SHORT_LABEL_MAX_HEADER);
    expect(cut.length).toBeLessThanOrEqual(SHORT_LABEL_MAX_HEADER);
    expect(cut.endsWith('…')).toBe(true);
  });
});
