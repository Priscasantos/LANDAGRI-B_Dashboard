import { useMemo, type ReactElement } from 'react';
import EChartsBase from './EChartsBase';
import { buildPolarOption, type PolarSeriesInput } from './echarts-options';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { useChartFontFamily } from '../../../hooks/use-chart-font';
import { useT } from '../../../i18n/LanguageContext';
import type { TKey } from '../../../i18n/types';

interface EChartsPolarProps {
  /** Same shape as the Plotly `PolarChart` series (fill is always on). */
  series: (PolarSeriesInput & { fill?: 'none' | 'toself' })[];
  /** Angle-axis categories (Plotly `theta` analogue). */
  categories: (string | number)[];
  /** i18n key in `charts` namespace for figcaption/aria-label. */
  captionKey?: TKey<'charts'>;
  height?: number;
}

export default function EChartsPolar({
  series,
  categories,
  captionKey,
  height = 450,
}: EChartsPolarProps): ReactElement {
  const theme = useEffectiveTheme();
  const fontFamily = useChartFontFamily();
  const { t, locale } = useT('charts');

  const option = useMemo(
    () => buildPolarOption({ categories, series, theme, locale, fontFamily }),
    [categories, series, theme, locale, fontFamily],
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
