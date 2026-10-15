import { useMemo, type ReactElement } from 'react';
import EChartsBase from './EChartsBase';
import { buildScatterOption, type ScatterSeriesInput } from './echarts-options';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { useChartFontFamily } from '../../../hooks/use-chart-font';
import { useT } from '../../../i18n/LanguageContext';
import type { TKey } from '../../../i18n/types';

interface EChartsScatterProps {
  series: ScatterSeriesInput[];
  /** i18n key in `charts` namespace for figcaption/aria-label. */
  captionKey?: TKey<'charts'>;
  height?: number;
  /** Y axis scale (Plotly `type: 'log'` analogue). */
  yAxisType?: 'value' | 'log';
}

export default function EChartsScatter({
  series,
  captionKey,
  height,
  yAxisType,
}: EChartsScatterProps): ReactElement {
  const theme = useEffectiveTheme();
  const fontFamily = useChartFontFamily();
  const { t, locale } = useT('charts');

  const option = useMemo(
    () => buildScatterOption({ series, theme, locale, fontFamily, yAxisType }),
    [series, theme, locale, fontFamily, yAxisType],
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
