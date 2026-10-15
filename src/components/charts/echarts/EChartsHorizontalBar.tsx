import { useMemo, type ReactElement } from 'react';
import EChartsBase from './EChartsBase';
import { buildHorizontalBarOption } from './echarts-options';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { useChartFontFamily } from '../../../hooks/use-chart-font';
import { useT } from '../../../i18n/LanguageContext';
import type { TKey } from '../../../i18n/types';

interface EChartsHorizontalBarProps {
  labels: (string | number)[];
  values: (number | null)[];
  /** i18n key in `charts` namespace for figcaption/aria-label. */
  captionKey?: TKey<'charts'>;
  color?: string;
  name?: string;
  height?: number;
}

export default function EChartsHorizontalBar({
  labels,
  values,
  captionKey,
  color,
  name,
  height,
}: EChartsHorizontalBarProps): ReactElement {
  const theme = useEffectiveTheme();
  const fontFamily = useChartFontFamily();
  const { t, locale } = useT('charts');

  const option = useMemo(
    () =>
      buildHorizontalBarOption({
        labels,
        values,
        theme,
        locale,
        fontFamily,
        color,
        name,
      }),
    [labels, values, theme, locale, fontFamily, color, name],
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
