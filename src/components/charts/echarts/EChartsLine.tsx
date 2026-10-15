import { useMemo, type ReactElement } from 'react';
import EChartsBase from './EChartsBase';
import { buildLineOption, type EChartsLinePoint } from './echarts-options';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { useChartFontFamily } from '../../../hooks/use-chart-font';
import { useT } from '../../../i18n/LanguageContext';
import type { TKey } from '../../../i18n/types';

interface EChartsLineProps {
  /** Same shape as the Plotly `LineChart` series (dash is not rendered). */
  series: (EChartsLinePoint & { dash?: 'solid' | 'dash' | 'dot' })[];
  /** i18n key in `charts` namespace for figcaption/aria-label. */
  captionKey?: TKey<'charts'>;
  height?: number;
  showMarkers?: boolean;
  /** Fill under the line (Plotly `fill="tozeroy"`). */
  areaFill?: boolean;
  /** Stack all series (Plotly `stackgroup` analogue). */
  stack?: boolean;
}

export default function EChartsLine({
  series,
  captionKey,
  height,
  showMarkers = true,
  areaFill = false,
  stack = false,
}: EChartsLineProps): ReactElement {
  const theme = useEffectiveTheme();
  const fontFamily = useChartFontFamily();
  const { t, locale } = useT('charts');

  const option = useMemo(
    () =>
      buildLineOption({
        series,
        theme,
        locale,
        fontFamily,
        showMarkers,
        areaFill,
        stack,
      }),
    [series, theme, locale, fontFamily, showMarkers, areaFill, stack],
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
