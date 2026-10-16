import { useMemo, type ReactElement } from 'react';
import EChartsBase from './EChartsBase';
import { buildPhenoGanttOption, type PhenoGanttSegment } from './echarts-options';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { useChartColorway } from '../../../hooks/use-chart-colorway';
import { useChartFontFamily } from '../../../hooks/use-chart-font';
import { useT } from '../../../i18n/LanguageContext';
import type { TKey } from '../../../i18n/types';

export interface EChartsPhenoGanttSegment extends PhenoGanttSegment {
  lane: number;
  start: number;
  end: number;
  ph: boolean;
  tip: string;
}

interface EChartsPhenoGanttProps {
  /** Rótulos das lanes P/H por cultura-região (eixo y). */
  lanes: string[];
  laneKinds: ('P' | 'H')[];
  /** Rótulos dos meses no eixo safra (Out→Set). */
  xLabels: (string | number)[];
  segments: EChartsPhenoGanttSegment[];
  /** Banda "safra vigente" (fim no eixo de valor) + linha "hoje". */
  seasonBandEnd: number;
  seasonBandName: string;
  todayPosition: number;
  todayName: string;
  /** i18n key in `charts` namespace for figcaption/aria-label. */
  captionKey?: TKey<'charts'>;
  height?: number;
}

/**
 * Gantt fenológico (Gaia): lanes P/H com segmentos disjuntos e hachura PH.
 */
export default function EChartsPhenoGantt({
  lanes,
  laneKinds,
  xLabels,
  segments,
  seasonBandEnd,
  seasonBandName,
  todayPosition,
  todayName,
  captionKey,
  height = 500,
}: EChartsPhenoGanttProps): ReactElement {
  const theme = useEffectiveTheme();
  const { colorway, preset: presetValue } = useChartColorway();
  const fontFamily = useChartFontFamily();
  const { t, locale } = useT('charts');

  const option = useMemo(
    () =>
      buildPhenoGanttOption({
        lanes,
        laneKinds,
        xLabels,
        segments,
        seasonBandEnd,
        seasonBandName,
        todayPosition,
        todayName,
        theme,
        colorway,
        preset: presetValue,
        locale,
        fontFamily,
      }),
    [lanes, laneKinds, xLabels, segments, seasonBandEnd, seasonBandName, todayPosition, todayName, theme, colorway, presetValue, locale, fontFamily],
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
