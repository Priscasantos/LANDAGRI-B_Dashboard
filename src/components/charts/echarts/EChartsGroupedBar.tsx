import { useMemo, type ReactElement } from 'react';
import EChartsBase from './EChartsBase';
import { buildGroupedBarOption, type GroupedBarSeriesInput } from './echarts-options';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { useChartColorway } from '../../../hooks/use-chart-colorway';
import { useChartFontFamily } from '../../../hooks/use-chart-font';
import { useT } from '../../../i18n/LanguageContext';
import type { TKey } from '../../../i18n/types';

interface EChartsGroupedBarProps {
  categories: (string | number)[];
  series: GroupedBarSeriesInput[];
  /** i18n key in `charts` namespace for figcaption/aria-label. */
  captionKey?: TKey<'charts'>;
  height?: number;
  /** Stack all series (Plotly `barmode: 'stack'` analogue). */
  stacked?: boolean;
  /** Dashed average line on the first series (caller resolves i18n). */
  referenceLine?: { value: number; name: string; color?: string };
  /** Y axis scale (Plotly `type: 'log'` analogue). */
  yAxisType?: 'value' | 'log';
  /**
   * Pre-formatted HTML tooltip per `[series][category]` (ex. listas de
   *   UFs). Omitido → tooltip padrão do eixo.
   */
  tips?: (string | null)[][];
}

export default function EChartsGroupedBar({
  categories,
  series,
  captionKey,
  height = 400,
  stacked,
  referenceLine,
  yAxisType,
  tips,
}: EChartsGroupedBarProps): ReactElement {
  const theme = useEffectiveTheme();
  const { colorway, preset: presetValue } = useChartColorway();
  const fontFamily = useChartFontFamily();
  const { t, locale } = useT('charts');

  const option = useMemo(
    () =>
      buildGroupedBarOption({
        categories,
        series,
        theme,
        colorway,
        preset: presetValue,
        locale,
        fontFamily,
        stacked,
        referenceLine,
        yAxisType,
        ...(tips !== undefined ? { tips } : {}),
      }),
    [categories, series, theme, colorway, presetValue, locale, fontFamily, stacked, referenceLine, yAxisType, tips],
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
