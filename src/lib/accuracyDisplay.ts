/**
 * Council unânime (reversível): IBGE-MLCU e CONAB-AM exibem "—/n.d." com
 * tooltip citando fontes, excluídos do Overall_Score com reponderação
 * transparente. Proxy MapBiomas rejeitado; 0.0 cru proibido no display
 * (0 interno = ausente, nunca renderizado).
 */

/** Literal exato do council para overall_accuracy ausente. */
export const ACCURACY_UNAVAILABLE_LABEL = '—/n.d.';

export interface AccuracySourceLink {
  label: string;
  url: string;
}

/**
 * Fontes citadas no tooltip (domínios do council; raízes estáveis, sem
 * deep-links inventados). IBGE-MLCU → cobertura e uso da terra;
 * CONAB-AM → CONAB + CSR-UFMG.
 */
export const ACCURACY_SOURCE_LINKS: Record<string, AccuracySourceLink[]> = {
  'IBGE-MLCU': [
    { label: 'IBGE — Cobertura e Uso da Terra', url: 'https://www.ibge.gov.br/geociencias' },
  ],
  'CONAB-AM': [
    { label: 'CONAB', url: 'https://www.gov.br/conab' },
    { label: 'CSR-UFMG/CONAB', url: 'https://csr.ufmg.br' },
  ],
};

export function sourceLinksFor(acronym: string): AccuracySourceLink[] {
  const direct = ACCURACY_SOURCE_LINKS[acronym];
  if (direct !== undefined) return direct;
  return Object.values(ACCURACY_SOURCE_LINKS).flat();
}

/** OA avaliado ⇔ valor interno > 0 (0 = ausente, nunca exibido). */
export function hasAssessedAccuracy(value: number): boolean {
  return value > 0;
}

/**
 * Célula com "%": `"91.0%"` quando avaliado, `"—/n.d."` caso contrário.
 * Nunca retorna `"0.0%"`/`"0.0"`.
 */
export function formatAccuracyPct(value: number, label?: string | undefined): string {
  if (value > 0) return `${value.toFixed(1)}%`;
  return label ?? ACCURACY_UNAVAILABLE_LABEL;
}

/** Rótulo sem "%" (cards/detalhe): `"91.0"` ou `"—/n.d."`. */
export function formatAccuracyValue(value: number, label?: string | undefined): string {
  if (value > 0) return value.toFixed(1);
  return label ?? ACCURACY_UNAVAILABLE_LABEL;
}

/**
 * Tooltip "Fonte não publica overall_accuracy" + links das fontes.
 * `noOverallPhrase` vem do i18n (`initiative.accuracyNoOverall`);
 * `sourceNote` é o motivo da fonte (Accuracy_Note do parser).
 */
export function accuracyTooltipText(
  noOverallPhrase: string,
  acronym: string,
  sourceNote?: string | undefined,
): string {
  const links = sourceLinksFor(acronym)
    .map((l) => `${l.label}: ${l.url}`)
    .join(' · ');
  const base = `${noOverallPhrase} — ${links}`;
  return sourceNote !== undefined && sourceNote !== '' ? `${base} (${sourceNote})` : base;
}

/**
 * Média sobre N válido (exclui sem OA publicado). Base do Overall_Score:
 * IBGE-MLCU e CONAB-AM (0 interno) nunca diluem a média. Retorna 0 quando
 * não há N válido — o chamador deve exibir "—/n.d." nesse caso.
 */
export function averageOverValid(values: number[]): number {
  const valid = values.filter((v) => v > 0);
  if (valid.length === 0) return 0;
  return valid.reduce((sum, v) => sum + v, 0) / valid.length;
}

/** Quantos valores entram no Overall_Score (N válido, transparente). */
export function countValid(values: number[]): number {
  return values.filter((v) => v > 0).length;
}
