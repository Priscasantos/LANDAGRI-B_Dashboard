import { useSyncExternalStore } from 'react';
import { getFontOption } from '../lib/fonts';

function subscribe(callback: () => void): () => void {
  const observer = new MutationObserver(callback);
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-font'],
  });
  return () => observer.disconnect();
}

function snapshot(): string {
  return document.documentElement.dataset.font ?? 'default';
}

/**
 * Família de fonte reativa dos gráficos (Fase 2 qualidade).
 *
 * Lê o `data-font` vigente na raiz (gravado pelo customizer via
 * `useThemeManager`) e re-renderiza quando ele muda, via MutationObserver
 * no `<html>`. Assim os charts ECharts refazem a opção com a fonte ativa
 * sem reload. Reversível: hook puro, sem estado global novo.
 */
export function useChartFontFamily(): string {
  const fontValue = useSyncExternalStore(subscribe, snapshot, () => 'default');
  return getFontOption(fontValue).sans;
}
