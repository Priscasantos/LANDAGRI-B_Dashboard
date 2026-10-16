import { useMemo, type ReactElement } from 'react';
import EChartsBase from './EChartsBase';
import { buildHeatmapOption } from './echarts-options';
import type { EChartsPalette } from '../../../lib/echarts-theme';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { useChartColorway } from '../../../hooks/use-chart-colorway';
import { useChartFontFamily } from '../../../hooks/use-chart-font';
import { useT } from '../../../i18n/LanguageContext';
import type { TKey } from '../../../i18n/types';

interface EChartsHeatmapProps {
  z: (number | null)[][];
  x: (string | number)[];
  y: (string | number)[];
  /** i18n key in `charts` namespace for figcaption/aria-label. */
  captionKey?: TKey<'charts'>;
  /** visualMap colors (Plotly `colorscale` analogue). */
  colors?: string[];
  /**
   * Explicit palette (default `'theme'`). Use `'divergent'` only where the
   * sign carries meaning (correlation −1…1); explicit `colors` wins.
   */
  palette?: EChartsPalette;
  /** visualMap bounds (Plotly `zmin`/`zmax` analogue). */
  min?: number;
  max?: number;
  /** Render values inside cells (Plotly `texttemplate` analogue). */
  showValues?: boolean;
  /** Value range on light cells (dark label text; white elsewhere). */
  labelDarkRange?: [number, number];
  /** Suffix for cell labels/tooltips (ex. `'%'` for share heatmaps). */
  valueSuffix?: string;
  /** Pre-formatted HTML tooltip per cell `[yi][xi]`; `null` → default. */
  tips?: (string | null)[][];
  height?: number;
}

export default function EChartsHeatmap({
  z,
  x,
  y,
  captionKey,
  height = 450,
  colors,
  palette,
  min,
  max,
  showValues,
  labelDarkRange,
  valueSuffix,
  tips,
}: EChartsHeatmapProps): ReactElement {
  const theme = useEffectiveTheme();
  const { colorway, preset: presetValue } = useChartColorway();
  const fontFamily = useChartFontFamily();
  const { t, locale } = useT('charts');

  const option = useMemo(
    () => buildHeatmapOption({ x, y, z, theme, colorway, preset: presetValue, locale, fontFamily, colors, palette, min, max, showValues, labelDarkRange, valueSuffix, tips }),
    [x, y, z, theme, colorway, presetValue, locale, fontFamily, colors, palette, min, max, showValues, labelDarkRange, valueSuffix, tips],
  );

  const caption = captionKey !== undefined ? t(captionKey) : '';
  return (
    <EChartsBase
      option={option}
      ariaLabel={caption === '' ? t('interactiveChart') : caption}
      caption={caption}
      height={height}
    />
  );
}
