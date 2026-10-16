/**
 * Codificação fenológica fixa cross-tab (Gaia — documenta o contrato).
 *
 * - COR = fase fenológica. Plantio = verde Agro; Colheita = âmbar/terra;
 *   PH (plantio e colheita simultâneos) = base da fase + hachura contrastante.
 * - Cultura e região NUNCA usam cor: distinguem-se pelo rótulo da faixa/eixo.
 * - Barras P/H agregadas (mensal, polar, sazonal) reutilizam estas cores —
 *   nenhum gráfico mistura "cor de cultura" com "cor de fase".
 */
import type { EChartsPilotTheme } from './echarts-theme';

export type PhenoPhase = 'P' | 'H';

/** Verde Agro do colorway do tema ativo (índice 0). */
export function phenoPhaseColor(phase: PhenoPhase, theme: EChartsPilotTheme): string {
  if (phase === 'P') return theme === 'dark' ? '#9CCC65' : '#2E7D32';
  return theme === 'dark' ? '#E8A04C' : '#C2701D';
}

/** Cor da hachura PH: o oposto da fase da lane (contraste documentado). */
export function phenoHatchColor(phase: PhenoPhase, theme: EChartsPilotTheme): string {
  return phenoPhaseColor(phase === 'P' ? 'H' : 'P', theme);
}
