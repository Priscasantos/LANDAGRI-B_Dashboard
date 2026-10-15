import BaseChart from './BaseChart';
import type { Data, Layout } from 'plotly.js';
import { CATEGORICAL_COLORS } from '../../types/theme';

interface PolarSeries {
  name: string;
  r: number[];
  theta: string[];
  fill?: 'none' | 'toself';
}

interface PolarChartProps {
  series: PolarSeries[];
  title?: string;
  height?: number;
  layout?: Partial<Layout>;
}

export default function PolarChart({
  series, title, height = 450, layout: extraLayout,
}: PolarChartProps) {
  const data: Data[] = series.map((s, i) => ({
    type: 'scatterpolar',
    r: s.r,
    theta: s.theta,
    name: s.name,
    fill: s.fill || 'toself',
    marker: { color: CATEGORICAL_COLORS[i % CATEGORICAL_COLORS.length] },
    line: { color: CATEGORICAL_COLORS[i % CATEGORICAL_COLORS.length], width: 2 },
    hovertemplate: '<b>%{theta}</b><br>%{r:,.1f}<extra></extra>',
  }));

  const layout: Partial<Layout> = {
    title: title ? { text: title, x: 0.5 } : undefined,
    showlegend: true,
    legend: { orientation: 'h', y: -0.28 },
    polar: {
      radialaxis: {
        visible: true,
        gridcolor: '#e5e7eb',
        linecolor: '#d1d5db',
      },
    },
    ...extraLayout,
  };

  return <BaseChart data={data} layout={layout} height={height} />;
}
