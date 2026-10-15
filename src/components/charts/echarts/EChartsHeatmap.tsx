import { useMemo, type ReactElement } from 'react';
import EChartsBase from './EChartsBase';
import { buildHeatmapOption } from './echarts-options';
import type { EChartsPalette } from '../../../lib/echarts-theme';
import { useEffectiveTheme } from '../../../hooks/use-theme';
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
}: EChartsHeatmapProps): ReactElement {
  const theme = useEffectiveTheme();
  const fontFamily = useChartFontFamily();
  const { t, locale } = useT('charts');

  const option = useMemo(
    () => buildHeatmapOption({ x, y, z, theme, locale, fontFamily, colors, palette, min, max, showValues, labelDarkRange }),
    [x, y, z, theme, locale, fontFamily, colors, palette, min, max, showValues, labelDarkRange],
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
