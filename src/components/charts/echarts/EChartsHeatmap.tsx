import { useMemo, type ReactElement } from 'react';
import EChartsBase from './EChartsBase';
import { buildHeatmapOption } from './echarts-options';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { useT } from '../../../i18n/LanguageContext';
import type { TKey } from '../../../i18n/types';

interface EChartsHeatmapProps {
  z: (number | null)[][];
  x: (string | number)[];
  y: (string | number)[];
  /** i18n key in `charts` namespace for figcaption/aria-label. */
  captionKey?: TKey<'charts'>;
  height?: number;
}

export default function EChartsHeatmap({
  z,
  x,
  y,
  captionKey,
  height = 450,
}: EChartsHeatmapProps): ReactElement {
  const theme = useEffectiveTheme();
  const { t, locale } = useT('charts');

  const option = useMemo(
    () => buildHeatmapOption({ x, y, z, theme, locale }),
    [x, y, z, theme, locale],
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
