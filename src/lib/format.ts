import type { Locale } from '../i18n/types';

function bcp47(locale: Locale): string {
  return locale === 'pt-BR' ? 'pt-BR' : 'en';
}

/**
 * Compacta um valor em milhares para exibição 1× no KPI.
 *
 * - `pt-BR`: `94928` → `"94,9 mil"` (decimal `,`, sufixo `mil`)
 * - `en`: `94928` → `"94.9k"` (decimal `.`, sufixo `k`)
 *
 * Uma única unidade compacta — nunca `"94.928k thousand"`. Valores
 * < 1000 saem como inteiro agrupado do locale, sem sufixo.
 */
export function formatCompactK(valueInThousands: number, locale: Locale): string {
  const abs = Math.abs(valueInThousands);
  if (abs < 1000) {
    return valueInThousands.toLocaleString(bcp47(locale), { maximumFractionDigits: 0 });
  }
  const compact = (valueInThousands / 1000).toLocaleString(bcp47(locale), {
    minimumFractionDigits: 0,
    maximumFractionDigits: 1,
  });
  return locale === 'pt-BR' ? `${compact} mil` : `${compact}k`;
}

/** Produção total (mil t): `"294,9 mil t"` / `"294.9k t"`. */
export function formatKpiProduction(totalProductionThousandTons: number, locale: Locale): string {
  return `${formatCompactK(totalProductionThousandTons, locale)}\u00a0t`;
}

/** Área plantada (mil ha): `"75,2 mil ha"` / `"75.2k ha"`. */
export function formatKpiArea(totalAreaThousandHectares: number, locale: Locale): string {
  return `${formatCompactK(totalAreaThousandHectares, locale)}\u00a0ha`;
}

/**
 * Produtividade média por hectare — unidade correta `kg/ha` (nunca `kg/h`),
 * inteiro agrupado pelo locale e espaço inseparável antes da unidade para
 * a dupla valor↔unidade não quebrar em duas linhas.
 */
export function formatProductivity(avgKgPerHectare: number, locale: Locale): string {
  const grouped = Math.round(avgKgPerHectare).toLocaleString(bcp47(locale));
  return `${grouped}\u00a0kg/ha`;
}
