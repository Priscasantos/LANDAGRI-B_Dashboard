import BaseChart from './BaseChart';
import type { Data, Layout } from 'plotly.js';
import { CATEGORICAL_COLORS } from '../../types/theme';

interface LineSeries {
  name: string;
  x: (string | number)[];
  y: (number | null)[];
  color?: string;
  dash?: 'solid' | 'dash' | 'dot';
}

interface LineChartProps {
  series: LineSeries[];
  title?: string;
  xlabel?: string;
  ylabel?: string;
  height?: number;
  showMarkers?: boolean;
  fill?: 'none' | 'tozeroy' | 'tonexty';
  layout?: Partial<Layout>;
}

export default function LineChart({
  series, title, xlabel, ylabel, height = 400,
  showMarkers = true, fill = 'none', layout: extraLayout,
}: LineChartProps) {
  const data: Data[] = series.map((s, i) => ({
    type: 'scatter',
    mode: showMarkers ? 'lines+markers' : 'lines',
    name: s.name,
    x: s.x,
    y: s.y,
    marker: { color: s.color || CATEGORICAL_COLORS[i % CATEGORICAL_COLORS.length], size: 6 },
    line: {
      color: s.color || CATEGORICAL_COLORS[i % CATEGORICAL_COLORS.length],
      dash: s.dash || 'solid',
      width: 2,
    },
    fill,
    fillcolor: 'rgba(59, 130, 246, 0.05)',
    hovertemplate: '<b>%{x}</b><br>' + s.name + ': %{y:,.1f}<extra></extra>',
  }));

  const { xaxis: extraXAxis, yaxis: extraYAxis, ...restExtraLayout } = extraLayout ?? {};

  const layout: Partial<Layout> = {
    title: title ? { text: title, x: 0.5 } : undefined,
    // Deep-merge axes so a caller override (e.g. integer-year ticks) keeps
    // the default title/tickangle instead of replacing the whole axis.
    xaxis: { title: { text: xlabel }, tickangle: -45, ...extraXAxis },
    yaxis: { title: { text: ylabel }, ...extraYAxis },
    showlegend: true,
    legend: { orientation: 'h', y: -0.3 },
    hovermode: 'x unified',
    ...restExtraLayout,
  };

  return <BaseChart data={data} layout={layout} height={height} />;
}
