import type { Locale } from '../i18n/types';

/**
 * Glossário Fase 1 — SÓ a UI é traduzida; dados nunca são re-fetchados.
 *
 * Nomes próprios de iniciativas (ex. "MapBiomas") permanecem intactos nos
 * dois locales; aqui vão enums e unidades exibidos na UI (cobertura,
 * metodologia, frequência temporal, unidades, cabeçalhos genéricos).
 * Valor fora do glossário retorna como veio (passthrough) — nunca some.
 */

export type GlossaryKind = 'coverage' | 'methodology' | 'frequency' | 'unit' | 'header';

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

const TABLES: Record<GlossaryKind, Record<string, LocalizedTerm>> = {
  coverage: COVERAGE,
  methodology: METHODOLOGY,
  frequency: FREQUENCY,
  unit: UNIT,
  header: HEADER,
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
  void locale; // nomes próprios invariantes por locale (documentado acima)
  return name;
}
