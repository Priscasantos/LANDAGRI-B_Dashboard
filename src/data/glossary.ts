import type { Locale } from '../i18n/types';

/**
 * Glossário Fase 1 — SÓ a UI é traduzida; dados nunca são re-fetchados.
 *
 * Nomes próprios de iniciativas (ex. "MapBiomas") permanecem intactos nos
 * dois locales; aqui vão enums e unidades exibidos na UI (cobertura,
 * metodologia, frequência temporal, unidades, cabeçalhos genéricos).
 * Valor fora do glossário retorna como veio (passthrough) — nunca some.
 */

export type GlossaryKind =
  | 'coverage'
  | 'methodology'
  | 'frequency'
  | 'unit'
  | 'header'
  | 'crop'
  | 'region'
  | 'month'
  | 'monthShort'
  | 'season'
  | 'activity';

type LocalizedTerm = Record<Locale, string>;

const COVERAGE: Record<string, LocalizedTerm> = {
  Global: { 'pt-BR': 'Global', en: 'Global' },
  Continental: { 'pt-BR': 'Continental', en: 'Continental' },
  National: { 'pt-BR': 'Nacional', en: 'National' },
  Regional: { 'pt-BR': 'Regional', en: 'Regional' },
  State: { 'pt-BR': 'Estadual', en: 'State' },
  Municipal: { 'pt-BR': 'Municipal', en: 'Municipal' },
  Local: { 'pt-BR': 'Local', en: 'Local' },
  Biome: { 'pt-BR': 'Bioma', en: 'Biome' },
};

const METHODOLOGY: Record<string, LocalizedTerm> = {
  Hybrid: { 'pt-BR': 'Híbrida', en: 'Hybrid' },
  'Deep Learning': { 'pt-BR': 'Aprendizado Profundo', en: 'Deep Learning' },
  'Machine Learning': { 'pt-BR': 'Aprendizado de Máquina', en: 'Machine Learning' },
  'Visual Interpretation': { 'pt-BR': 'Interpretação Visual', en: 'Visual Interpretation' },
  Supervised: { 'pt-BR': 'Supervisionada', en: 'Supervised' },
  Unsupervised: { 'pt-BR': 'Não supervisionada', en: 'Unsupervised' },
};

const FREQUENCY: Record<string, LocalizedTerm> = {
  Annual: { 'pt-BR': 'Anual', en: 'Annual' },
  'Annual and Seasonal': { 'pt-BR': 'Anual e Sazonal', en: 'Annual and Seasonal' },
  Biennial: { 'pt-BR': 'Bienal', en: 'Biennial' },
  'Biennial since 2010': { 'pt-BR': 'Bienal desde 2010', en: 'Biennial since 2010' },
  'By Crop Year': { 'pt-BR': 'Por Ano-Safra', en: 'By Crop Year' },
  Quadriennial: { 'pt-BR': 'Quadrienal', en: 'Quadrennial' },
};

const UNIT: Record<string, LocalizedTerm> = {
  ha: { 'pt-BR': 'ha', en: 'ha' },
  'km²': { 'pt-BR': 'km²', en: 'km²' },
  m: { 'pt-BR': 'm', en: 'm' },
  '%': { 'pt-BR': '%', en: '%' },
  px: { 'pt-BR': 'px', en: 'px' },
  year: { 'pt-BR': 'ano', en: 'year' },
  years: { 'pt-BR': 'anos', en: 'years' },
  classes: { 'pt-BR': 'classes', en: 'classes' },
};

const HEADER: Record<string, LocalizedTerm> = {
  initiative: { 'pt-BR': 'Iniciativa', en: 'Initiative' },
  acronym: { 'pt-BR': 'Sigla', en: 'Acronym' },
  coverage: { 'pt-BR': 'Cobertura', en: 'Coverage' },
  methodology: { 'pt-BR': 'Metodologia', en: 'Methodology' },
  provider: { 'pt-BR': 'Provedor', en: 'Provider' },
  sensor: { 'pt-BR': 'Sensor', en: 'Sensor' },
  source: { 'pt-BR': 'Fonte', en: 'Source' },
  years: { 'pt-BR': 'Anos', en: 'Years' },
  resolution: { 'pt-BR': 'Resolução', en: 'Resolution' },
  accuracy: { 'pt-BR': 'Acurácia', en: 'Accuracy' },
};

/**
 * Culturas vindas dos dados (CONAB/conab_calendar/conab_availability).
 * Chave = rótulo EN após normalização de ordinais ("3th"→"3rd");
 * dados brutos seguem intactos — tradução só na exibição.
 */
const CROP: Record<string, LocalizedTerm> = {
  Soybean: { 'pt-BR': 'Soja', en: 'Soybean' },
  Corn: { 'pt-BR': 'Milho', en: 'Corn' },
  'Corn (1st harvest)': { 'pt-BR': 'Milho (1ª safra)', en: 'Corn (1st harvest)' },
  'Corn (2nd harvest)': { 'pt-BR': 'Milho (2ª safra)', en: 'Corn (2nd harvest)' },
  'Corn (3rd harvest)': { 'pt-BR': 'Milho (3ª safra)', en: 'Corn (3rd harvest)' },
  'Corn (1st + 2nd harvest)': {
    'pt-BR': 'Milho (1ª + 2ª safra)',
    en: 'Corn (1st + 2nd harvest)',
  },
  'Corn (Total)': { 'pt-BR': 'Milho (Total)', en: 'Corn (Total)' },
  Cotton: { 'pt-BR': 'Algodão', en: 'Cotton' },
  Rice: { 'pt-BR': 'Arroz', en: 'Rice' },
  'Irrigated Rice': { 'pt-BR': 'Arroz Irrigado', en: 'Irrigated Rice' },
  Beans: { 'pt-BR': 'Feijão', en: 'Beans' },
  'Beans (1st harvest)': { 'pt-BR': 'Feijão (1ª safra)', en: 'Beans (1st harvest)' },
  'Beans (2nd harvest)': { 'pt-BR': 'Feijão (2ª safra)', en: 'Beans (2nd harvest)' },
  'Beans (3rd harvest)': { 'pt-BR': 'Feijão (3ª safra)', en: 'Beans (3rd harvest)' },
  'Beans (1st + 2nd + 3rd harvest)': {
    'pt-BR': 'Feijão (1ª + 2ª + 3ª safra)',
    en: 'Beans (1st + 2nd + 3rd harvest)',
  },
  Wheat: { 'pt-BR': 'Trigo', en: 'Wheat' },
  Sorghum: { 'pt-BR': 'Sorgo', en: 'Sorghum' },
  Sunflower: { 'pt-BR': 'Girassol', en: 'Sunflower' },
  Peanut: { 'pt-BR': 'Amendoim', en: 'Peanut' },
  'Peanut (1st harvest)': { 'pt-BR': 'Amendoim (1ª safra)', en: 'Peanut (1st harvest)' },
  Coffee: { 'pt-BR': 'Café', en: 'Coffee' },
  'Sugar cane': { 'pt-BR': 'Cana-de-açúcar', en: 'Sugar cane' },
  'Sugar cane mill': { 'pt-BR': 'Usina de cana-de-açúcar', en: 'Sugar cane mill' },
  'Other summer crops': { 'pt-BR': 'Outras culturas de verão', en: 'Other summer crops' },
  'Other winter crops': {
    'pt-BR': 'Outras culturas de inverno',
    en: 'Other winter crops',
  },
  // Rótulos IBGE (nomes PT originais confirmados em
  // data/brazilian_agricultural_data.json → producao_agricola[].nome).
  'Peanut (in shell)': { 'pt-BR': 'Amendoim (em casca)', en: 'Peanut (in shell)' },
  'Rice (in husk)': { 'pt-BR': 'Arroz (em casca)', en: 'Rice (in husk)' },
  Oat: { 'pt-BR': 'Aveia', en: 'Oat' },
  'Oat (grain)': { 'pt-BR': 'Aveia (em grão)', en: 'Oat (grain)' },
  'Sweet potato': { 'pt-BR': 'Batata-doce', en: 'Sweet potato' },
  Potato: { 'pt-BR': 'Batata-inglesa', en: 'Potato' },
  Sugarcane: { 'pt-BR': 'Cana-de-açúcar', en: 'Sugarcane' },
  Cassava: { 'pt-BR': 'Mandioca', en: 'Cassava' },
  'Corn (grain)': { 'pt-BR': 'Milho (em grão)', en: 'Corn (grain)' },
  'Soybean (grain)': { 'pt-BR': 'Soja (em grão)', en: 'Soybean (grain)' },
  'Wheat (grain)': { 'pt-BR': 'Trigo (em grão)', en: 'Wheat (grain)' },
  'Cotton (lint and seed)': {
    'pt-BR': 'Algodão herbáceo (em caroço)',
    en: 'Cotton (lint and seed)',
  },
};

/** Regiões vindas dos dados (states[].region, filtros do calendário). */
const REGION: Record<string, LocalizedTerm> = {
  North: { 'pt-BR': 'Norte', en: 'North' },
  Northeast: { 'pt-BR': 'Nordeste', en: 'Northeast' },
  'Central-West': { 'pt-BR': 'Centro-Oeste', en: 'Central-West' },
  Midwest: { 'pt-BR': 'Centro-Oeste', en: 'Midwest' },
  Southeast: { 'pt-BR': 'Sudeste', en: 'Southeast' },
  South: { 'pt-BR': 'Sul', en: 'South' },
  Country: { 'pt-BR': 'Brasil', en: 'Country' },
};

/** Meses por extenso (conab_mapping seasons, cabeçalhos do calendário). */
const MONTH: Record<string, LocalizedTerm> = {
  January: { 'pt-BR': 'Janeiro', en: 'January' },
  February: { 'pt-BR': 'Fevereiro', en: 'February' },
  March: { 'pt-BR': 'Março', en: 'March' },
  April: { 'pt-BR': 'Abril', en: 'April' },
  May: { 'pt-BR': 'Maio', en: 'May' },
  June: { 'pt-BR': 'Junho', en: 'June' },
  July: { 'pt-BR': 'Julho', en: 'July' },
  August: { 'pt-BR': 'Agosto', en: 'August' },
  September: { 'pt-BR': 'Setembro', en: 'September' },
  October: { 'pt-BR': 'Outubro', en: 'October' },
  November: { 'pt-BR': 'Novembro', en: 'November' },
  December: { 'pt-BR': 'Dezembro', en: 'December' },
};

/** Meses abreviados (eixos/ticktext dos gráficos). */
const MONTH_SHORT: Record<string, LocalizedTerm> = {
  Jan: { 'pt-BR': 'Jan', en: 'Jan' },
  Feb: { 'pt-BR': 'Fev', en: 'Feb' },
  Mar: { 'pt-BR': 'Mar', en: 'Mar' },
  Apr: { 'pt-BR': 'Abr', en: 'Apr' },
  May: { 'pt-BR': 'Mai', en: 'May' },
  Jun: { 'pt-BR': 'Jun', en: 'Jun' },
  Jul: { 'pt-BR': 'Jul', en: 'Jul' },
  Aug: { 'pt-BR': 'Ago', en: 'Aug' },
  Sep: { 'pt-BR': 'Set', en: 'Sep' },
  Oct: { 'pt-BR': 'Out', en: 'Oct' },
  Nov: { 'pt-BR': 'Nov', en: 'Nov' },
  Dec: { 'pt-BR': 'Dez', en: 'Dec' },
};

/** Estações (SeasonalOverviewTab + metadata seasons). */
const SEASON: Record<string, LocalizedTerm> = {
  Spring: { 'pt-BR': 'Primavera', en: 'Spring' },
  Summer: { 'pt-BR': 'Verão', en: 'Summer' },
  Autumn: { 'pt-BR': 'Outono', en: 'Autumn' },
  Winter: { 'pt-BR': 'Inverno', en: 'Winter' },
  'Spring (Oct-Dec)': { 'pt-BR': 'Primavera (Out-Dez)', en: 'Spring (Oct-Dec)' },
  'Summer (Jan-Mar)': { 'pt-BR': 'Verão (Jan-Mar)', en: 'Summer (Jan-Mar)' },
  'Autumn (Apr-Jun)': { 'pt-BR': 'Outono (Abr-Jun)', en: 'Autumn (Apr-Jun)' },
  'Winter (Jul-Sep)': { 'pt-BR': 'Inverno (Jul-Set)', en: 'Winter (Jul-Sep)' },
};

/** Atividades/legendas vindas dos dados (P/H/PH, nomes de série). */
const ACTIVITY: Record<string, LocalizedTerm> = {
  Planting: { 'pt-BR': 'Plantio', en: 'Planting' },
  Harvest: { 'pt-BR': 'Colheita', en: 'Harvest' },
  'Planting and Harvest': { 'pt-BR': 'Plantio e Colheita', en: 'Planting and Harvest' },
  'Total Activity': { 'pt-BR': 'Atividade Total', en: 'Total Activity' },
  'Activity Intensity': { 'pt-BR': 'Intensidade de Atividade', en: 'Activity Intensity' },
  'Peak Intensity': { 'pt-BR': 'Pico de Intensidade', en: 'Peak Intensity' },
  'Total Production (thousand tons)': {
    'pt-BR': 'Produção Total (mil toneladas)',
    en: 'Total Production (thousand tons)',
  },
  'Total Production (tonnes)': {
    'pt-BR': 'Produção Total (toneladas)',
    en: 'Total Production (tonnes)',
  },
  'Harvested Area (hectares)': {
    'pt-BR': 'Área Colhida (hectares)',
    en: 'Harvested Area (hectares)',
  },
};

const TABLES: Record<GlossaryKind, Record<string, LocalizedTerm>> = {
  coverage: COVERAGE,
  methodology: METHODOLOGY,
  frequency: FREQUENCY,
  unit: UNIT,
  header: HEADER,
  crop: CROP,
  region: REGION,
  month: MONTH,
  monthShort: MONTH_SHORT,
  season: SEASON,
  activity: ACTIVITY,
};

/** Traduz um enum/unidade/cabeçalho; desconhecido volta intacto. */
export function translateTerm(
  kind: GlossaryKind,
  value: string,
  locale: Locale,
): string {
  return TABLES[kind][value]?.[locale] ?? value;
}

/**
 * Nome de exibição da iniciativa por locale — SEM duplicar fetch.
 * Nomes próprios ficam como estão (MapBiomas, PRODES…); o hook
 * `useInitiativeDisplayName` resolve no render a partir do locale ativo.
 */
export function getInitiativeDisplayName(name: string, locale: Locale): string {
  return translateInitiativeName(name, locale);
}

/**
 * Nome de iniciativa para exibição por locale (só display; bruto intacto).
 * Nomes próprios ficam como estão (MapBiomas, PRODES…), exceto o topônimo:
 * em PT usa-se "Brasil"/"Biomas Brasileiros" ("Brazil"/"Brazilian" só em
 * EN). Desconhecido volta intacto — nunca some.
 */
export function translateInitiativeName(name: string, locale: Locale): string {
  if (locale === 'en') return name;
  return name
    .replace(/\bBrazilian Biomes\b/g, 'Biomas Brasileiros')
    .replace(/\bBrazil\b/g, 'Brasil');
}

/**
 * Correções de typos em methodology names vindos dos dados (só display;
 * JSON bruto intacto):
 * - "Bhattacharya" → "Bhattacharyya" (distância de Bhattacharyya);
 * - "U-Net Deep learning" → "U-Net Deep Learning" (caixa consistente).
 * Cai para o enum de metodologia traduzido e, por fim, passthrough.
 */
const METHODOLOGY_FIX: Record<string, LocalizedTerm> = {
  'Visual Interpretation, Supervised Bhattacharya Classification, and Deep Learning': {
    'pt-BR':
      'Interpretação Visual, Classificação Supervisionada Bhattacharyya e Aprendizado Profundo',
    en: 'Visual Interpretation, Supervised Bhattacharyya Classification, and Deep Learning',
  },
  'Supervised Random Forest and U-Net Deep learning algorithms applied to Landsat series data': {
    'pt-BR':
      'Floresta Aleatória Supervisionada e algoritmos U-Net de Aprendizado Profundo aplicados a séries Landsat',
    en: 'Supervised Random Forest and U-Net Deep Learning algorithms applied to Landsat series data',
  },
};

/** Metodologia para exibição (typos corrigidos + tradução PT). */
export function translateMethodology(value: string, locale: Locale): string {
  const fixed = METHODOLOGY_FIX[value]?.[locale];
  if (fixed) return fixed;
  return TABLES.methodology[value]?.[locale] ?? value;
}

/**
 * Nome curto por iniciativa — sigla + nome curto traduzido (só display;
 * bruto intacto). Uso: cards, legendas, tooltips, eixos e tabela; o nome
 * completo (via `translateInitiativeName`) fica só no detalhe/popup.
 * Iniciativa fora da tabela volta intacta — nunca some.
 */
const INITIATIVE_SHORT: Record<string, { acronym: string; short: LocalizedTerm }> = {
  'Copernicus Global Land Cover Service Dynamic Land Cover': {
    acronym: 'CGLS',
    short: { 'pt-BR': 'Solo dinâmico Copernicus', en: 'Copernicus dynamic land' },
  },
  'Google Dynamic World V1': {
    acronym: 'GDW',
    short: { 'pt-BR': 'Mundo dinâmico Google', en: 'Google dynamic world' },
  },
  'ESRI-10m Annual LULC': {
    acronym: 'ESRI-10m LULC',
    short: { 'pt-BR': 'Uso do solo anual ESRI', en: 'ESRI annual LULC' },
  },
  'Global LULC change 2000 and 2020': {
    acronym: 'UMD-GLC',
    short: { 'pt-BR': 'Mudança global do solo', en: 'Global LULC change' },
  },
  'Global Pasture Watch (GPW)': {
    acronym: 'GPW',
    short: { 'pt-BR': 'Pastagens globais', en: 'Global pastures' },
  },
  'South America Soybean Maps': {
    acronym: 'UMD-SASM',
    short: { 'pt-BR': 'Soja na América do Sul', en: 'South American soybean' },
  },
  'WorldCover 10m 2021': {
    acronym: 'ESA-WC',
    short: { 'pt-BR': 'Cobertura global 2021', en: 'Global cover 2021' },
  },
  WorldCereal: {
    acronym: 'WorldCereal',
    short: { 'pt-BR': 'Cereais no mundo', en: 'World cereals' },
  },
  'PRODES Deforestation, Warnings and Vegetation for Brazilian Biomes': {
    acronym: 'PRODES',
    short: { 'pt-BR': 'Desmatamento e vegetação', en: 'Deforestation and vegetation' },
  },
  'DETER Deforestation, Warnings and Vegetation for Brazilian Biomes': {
    acronym: 'DETER',
    short: { 'pt-BR': 'Alertas de desmatamento', en: 'Deforestation warnings' },
  },
  'TerraClass Amazonia': {
    acronym: 'TerraClass Amazon',
    short: { 'pt-BR': 'Uso do solo na Amazônia', en: 'Amazon land use' },
  },
  'TerraClass Cerrado': {
    acronym: 'TerraClass Cerrado',
    short: { 'pt-BR': 'Uso do solo no Cerrado', en: 'Cerrado land use' },
  },
  MapBiomas: {
    acronym: 'MapBiomas',
    short: { 'pt-BR': 'Mapeamento anual do Brasil', en: 'Annual mapping of Brazil' },
  },
  'IBGE Monitoring Land Cover and Land Use': {
    acronym: 'IBGE-MLCU',
    short: { 'pt-BR': 'Cobertura e uso do solo IBGE', en: 'IBGE land cover and use' },
  },
  'National Supply Company Agricultural Mapping': {
    acronym: 'CONAB-AM',
    short: { 'pt-BR': 'Mapeamento agrícola CONAB', en: 'CONAB agricultural mapping' },
  },
};

/** Rótulo curto "SIGLA · nome curto" para cards/legendas/tooltips/tabela. */
export function getInitiativeShortName(name: string, locale: Locale): string {
  const direct = INITIATIVE_SHORT[name];
  if (direct) return `${direct.acronym} · ${direct.short[locale]}`;
  // `Display_Name` compõe "Nome (SIGLA)" (ver `dataParser`); resolve pela
  // base para a forma composta também encurtar (ex. "TerraClass Amazonia
  // (TerraClass Amazon)" → "TerraClass Amazon · Uso do solo na Amazônia").
  const base = name.replace(/\s*\([^()]*\)\s*$/, '');
  const entry = base !== name ? INITIATIVE_SHORT[base] : undefined;
  if (entry) return `${entry.acronym} · ${entry.short[locale]}`;
  return translateInitiativeName(name, locale);
}

/**
 * Normalização de ordinais dos dados CONAB ("3th harvest"→"3rd harvest").
 * Fonte única da verdade — `src/lib/cropNames.ts` delega para cá.
 * Arquivos-fonte preservados; só o rótulo exibido é corrigido.
 */
export function normalizeCropOrdinals(name: string): string {
  return name
    .replace(/\b1th\b/g, '1st')
    .replace(/\b2th\b/g, '2nd')
    .replace(/\b3th\b/g, '3rd');
}

/**
 * Nome de cultura para exibição: corrige ordinais e traduz quando
 * pt-BR; em EN devolve o original (só com ordinais normalizados).
 * Desconhecido volta intacto — nunca some.
 */
export function translateCropName(name: string, locale: Locale): string {
  const normalized = normalizeCropOrdinals(name);
  if (locale === 'en') return normalized;
  return CROP[normalized]?.['pt-BR'] ?? normalized;
}

/** Região para exibição (North→Norte…); desconhecida volta intacta. */
export function translateRegion(region: string, locale: Locale): string {
  return TABLES.region[region]?.[locale] ?? region;
}

/** Mês por extenso para exibição (October→Outubro…). */
export function translateMonth(month: string, locale: Locale): string {
  return TABLES.month[month]?.[locale] ?? month;
}

/** Mês abreviado para exibição (Oct→Out, Sep→Set…). */
export function translateMonthShort(month: string, locale: Locale): string {
  return TABLES.monthShort[month]?.[locale] ?? month;
}

/** Estação para exibição (Spring (Oct-Dec)→Primavera (Out-Dez)…). */
export function translateSeason(season: string, locale: Locale): string {
  return TABLES.season[season]?.[locale] ?? season;
}

/** Atividade para exibição (Planting→Plantio, Harvest→Colheita…). */
export function translateActivity(activity: string, locale: Locale): string {
  return TABLES.activity[activity]?.[locale] ?? activity;
}
