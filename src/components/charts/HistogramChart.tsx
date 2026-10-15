import BaseChart from './BaseChart';
import type { Data } from 'plotly.js';
import { useT } from '../../i18n/LanguageContext';

interface HistogramChartProps {
  x: number[];
  name?: string;
  xLabel?: string;
  yLabel?: string;
  title?: string;
  color?: string;
  height?: number;
  nbinsx?: number;
  opacity?: number;
  showlegend?: boolean;
}

export default function HistogramChart({
  x, name, xLabel, yLabel, title, color, height,
  nbinsx, opacity = 0.7, showlegend = true,
}: HistogramChartProps) {
  const { t } = useT('charts');
  const trace: Data = {
    name,
    x,
    type: 'histogram',
    marker: { color: color || '#3b82f6' },
    opacity,
    nbinsx,
    hovertemplate: `<b>${t('range')}: %{x}</b><br>${t('count')}: %{y}<extra></extra>`,
  };

  return (
    <BaseChart
      data={[trace]}
      layout={{
        title: { text: title || '', x: 0 },
        xaxis: { title: { text: xLabel } },
        yaxis: { title: { text: yLabel } },
        bargap: 0.1,
        showlegend,
        ...(height ? { height } : {}),
      }}
    />
  );
}
