import { useMemo, type ReactElement } from 'react';
import EChartsBase from './EChartsBase';
import { buildGanttOption } from './echarts-options';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { useChartColorway } from '../../../hooks/use-chart-colorway';
import { useChartFontFamily } from '../../../hooks/use-chart-font';
import { useT } from '../../../i18n/LanguageContext';
import type { TKey } from '../../../i18n/types';

export interface EChartsGanttBar {
  label: string;
  start: number;
  end: number;
  category?: string;
  color?: string;
  /** Pre-formatted tooltip body; defaults to `<b>label</b><br>period: start - end`. */
  tip?: string;
}

interface EChartsGanttProps {
  /** Month (or period) labels for the x value axis. */
  xLabels: (string | number)[];
  /** Same shape as the Plotly `GanttChart` bars. */
  bars: EChartsGanttBar[];
  /** i18n key in `charts` namespace for figcaption/aria-label. */
  captionKey?: TKey<'charts'>;
  height?: number;
  /** Vertical current-month line (Fase 2, value-axis position). */
  markLineX?: { position: number; name: string; color?: string };
}

export default function EChartsGantt({
  xLabels,
  bars,
  captionKey,
  height = 500,
  markLineX,
}: EChartsGanttProps): ReactElement {
  const theme = useEffectiveTheme();
  const { colorway, preset: presetValue } = useChartColorway();
  const fontFamily = useChartFontFamily();
  const { t, locale } = useT('charts');

  const option = useMemo(
    () =>
      buildGanttOption({
        xLabels,
        bars: bars.map((b) => ({
          y: b.label,
          start: b.start,
          duration: Math.max(b.end - b.start, 0),
          color: b.color,
          name: b.category ?? b.label,
          tip: b.tip ?? `<b>${b.label}</b><br>${t('period')}: ${b.start} - ${b.end}`,
        })),
        theme,
        colorway,
        preset: presetValue,
        locale,
        fontFamily,
        ...(markLineX !== undefined ? { markLineX } : {}),
      }),
    [xLabels, bars, theme, colorway, presetValue, locale, fontFamily, t, markLineX],
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
