import * as React from 'react';
import { DEFAULT_PRESET } from '../config/theme-presets';
import { presetCharts } from '../lib/chart-preset';
import type { EChartsPalette, EChartsPilotTheme } from '../lib/echarts-theme';
import { useEffectiveTheme } from './use-theme';

const CHART_SLOTS = 10;

function readChartVar(index: number): string {
  if (typeof document === 'undefined' || typeof getComputedStyle !== 'function') return '';
  return getComputedStyle(document.documentElement)
    .getPropertyValue(`--color-chart-${index}`)
    .trim();
}

function readPreset(): string {
  if (typeof document === 'undefined') return DEFAULT_PRESET;
  return document.documentElement.dataset.preset ?? DEFAULT_PRESET;
}

function readPaletteSetting(): EChartsPalette {
  if (typeof document === 'undefined') return 'theme';
  return document.documentElement.dataset.palette === 'divergent' ? 'divergent' : 'theme';
}

/**
 * Colorway categórica resolvida (jsdom/SSR-safe, pura o bastante p/ teste).
 *
 * Fonte 1: `--color-chart-1..10` computadas (seguem preset + light/dark via
 * `applyToRoot`, inclusive no modo divergente da sidebar — charts usam os
 * mesmos tokens). Fonte 2 (fallback): `presetCharts(preset, theme)` quando
 * as vars estão vazias (jsdom sem CSS, primeiro paint).
 */
export function readChartColorway(
  theme: EChartsPilotTheme,
  preset: string = readPreset(),
): string[] {
  const fromCss = Array.from({ length: CHART_SLOTS }, (_, k) => readChartVar(k + 1));
  if (fromCss.every((v) => v !== '')) return fromCss;
  return presetCharts(preset, theme);
}

export interface ChartColorway {
  /** 10 stops categóricos do preset ativo (light/dark resolvidos). */
  colorway: string[];
  /** Valor do preset ativo (`'agro-v2'`, `'terra'`, …). */
  preset: string;
  /** Tema efetivo. */
  theme: EChartsPilotTheme;
  /**
   * Paleta global da raiz (`data-palette`): `'theme'` default; `'divergent'`
   * realça a sidebar em alto contraste por preset. Charts analíticos
   * recebem `palette` explícito por gráfico (heatmap correlação, barras de
   * delta) — nunca herdam este global automaticamente, para não codificar
   * sinal onde só há magnitude.
   */
  paletteSetting: EChartsPalette;
}

/**
 * Colorway reativa do preset ativo — wrappers ECharts passam `colorway` +
 * `preset` aos builders para que os gráficos sigam preset + light/dark
 * (antes: constantes Verde Agro fixas). Re-renderiza em troca de tema,
 * preset ou paleta (MutationObserver nos atributos da raiz).
 */
export function useChartColorway(): ChartColorway {
  const theme = useEffectiveTheme();
  const [tick, setTick] = React.useState(0);

  React.useEffect(() => {
    if (typeof MutationObserver === 'undefined') return;
    const observer = new MutationObserver(() => setTick((t) => t + 1));
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class', 'style', 'data-preset', 'data-palette'],
    });
    return () => observer.disconnect();
  }, []);

  return React.useMemo(() => {
    const preset = readPreset();
    // `tick` é gatilho intencional de releitura pós-mutação da raiz.
    void tick;
    return {
      colorway: readChartColorway(theme, preset),
      preset,
      theme,
      paletteSetting: readPaletteSetting(),
    };
  }, [theme, tick]);
}
