import { useMemo, type ReactElement } from 'react';
import EChartsBase from './EChartsBase';
import { buildGroupedBarOption } from './echarts-options';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { useT } from '../../../i18n/LanguageContext';
import type { TKey } from '../../../i18n/types';

interface EChartsGroupedBarProps {
  categories: (string | number)[];
  series: { name: string; values: (number | null)[] }[];
  /** i18n key in `charts` namespace for figcaption/aria-label. */
  captionKey?: TKey<'charts'>;
  height?: number;
}

export default function EChartsGroupedBar({
  categories,
  series,
  captionKey,
  height = 400,
}: EChartsGroupedBarProps): ReactElement {
  const theme = useEffectiveTheme();
  const { t, locale } = useT('charts');

  const option = useMemo(
    () => buildGroupedBarOption({ categories, series, theme, locale }),
    [categories, series, theme, locale],
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
