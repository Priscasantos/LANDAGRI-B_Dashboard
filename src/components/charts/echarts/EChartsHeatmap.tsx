import { useMemo, type ReactElement } from 'react';
import EChartsBase from './EChartsBase';
import { buildHeatmapOption } from './echarts-options';
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
  /** visualMap bounds (Plotly `zmin`/`zmax` analogue). */
  min?: number;
  max?: number;
  /** Render values inside cells (Plotly `texttemplate` analogue). */
  showValues?: boolean;
  height?: number;
}

export default function EChartsHeatmap({
  z,
  x,
  y,
  captionKey,
  height = 450,
  colors,
  min,
  max,
  showValues,
}: EChartsHeatmapProps): ReactElement {
  const theme = useEffectiveTheme();
  const fontFamily = useChartFontFamily();
  const { t, locale } = useT('charts');

  const option = useMemo(
    () => buildHeatmapOption({ x, y, z, theme, locale, fontFamily, colors, min, max, showValues }),
    [x, y, z, theme, locale, fontFamily, colors, min, max, showValues],
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
