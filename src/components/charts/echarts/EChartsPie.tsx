import { useMemo, type ReactElement } from 'react';
import EChartsBase from './EChartsBase';
import { buildPieOption, type PieSliceInput } from './echarts-options';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { useChartColorway } from '../../../hooks/use-chart-colorway';
import { useChartFontFamily } from '../../../hooks/use-chart-font';
import { useT } from '../../../i18n/LanguageContext';
import type { TKey } from '../../../i18n/types';

interface EChartsPieProps {
  /** Same shape as the Plotly `PieChart` data. */
  data: PieSliceInput[];
  /** i18n key in `charts` namespace for figcaption/aria-label. */
  captionKey?: TKey<'charts'>;
  height?: number;
  donut?: boolean;
}

export default function EChartsPie({
  data,
  captionKey,
  height,
  donut = false,
}: EChartsPieProps): ReactElement {
  const theme = useEffectiveTheme();
  const { colorway, preset: presetValue } = useChartColorway();
  const fontFamily = useChartFontFamily();
  const { t, locale } = useT('charts');

  const option = useMemo(
    () =>
      buildPieOption({ slices: data, theme, colorway, preset: presetValue, locale, fontFamily, donut }),
    [data, theme, colorway, presetValue, locale, fontFamily, donut],
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
