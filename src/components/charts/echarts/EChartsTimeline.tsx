import { useMemo, type ReactElement } from 'react';
import EChartsBase from './EChartsBase';
import { buildTimelineOption, type TimelineItemInput } from './echarts-options';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { useChartFontFamily } from '../../../hooks/use-chart-font';
import { useT } from '../../../i18n/LanguageContext';
import type { TKey } from '../../../i18n/types';

interface EChartsTimelineProps {
  /** One entry per initiative (years + color + tooltip). */
  items: TimelineItemInput[];
  /** i18n key in `charts` namespace for figcaption/aria-label. */
  captionKey?: TKey<'charts'>;
  height?: number;
}

export default function EChartsTimeline({
  items,
  captionKey,
  height = 520,
}: EChartsTimelineProps): ReactElement {
  const theme = useEffectiveTheme();
  const fontFamily = useChartFontFamily();
  const { t, locale } = useT('charts');

  const option = useMemo(
    () => buildTimelineOption({ items, theme, locale, fontFamily }),
    [items, theme, locale, fontFamily],
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
