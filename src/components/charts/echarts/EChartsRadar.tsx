import { useMemo, type ReactElement } from 'react';
import EChartsBase from './EChartsBase';
import { buildRadarOption, type RadarSeriesInput } from './echarts-options';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { useChartColorway } from '../../../hooks/use-chart-colorway';
import { useChartFontFamily } from '../../../hooks/use-chart-font';
import { useT } from '../../../i18n/LanguageContext';
import type { TKey } from '../../../i18n/types';

interface EChartsRadarProps {
  indicators: string[];
  series: RadarSeriesInput[];
  /** i18n key in `charts` namespace for figcaption/aria-label. */
  captionKey?: TKey<'charts'>;
  height?: number;
}

export default function EChartsRadar({
  indicators,
  series,
  captionKey,
  height,
}: EChartsRadarProps): ReactElement {
  const theme = useEffectiveTheme();
  const { colorway, preset: presetValue } = useChartColorway();
  const fontFamily = useChartFontFamily();
  const { t, locale } = useT('charts');

  const option = useMemo(
    () => buildRadarOption({ indicators, series, theme, colorway, preset: presetValue, locale, fontFamily }),
    [indicators, series, theme, colorway, presetValue, locale, fontFamily],
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
