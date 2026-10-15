import BaseChart from './BaseChart';
import type { Data, Layout } from 'plotly.js';
import { CATEGORICAL_COLORS } from '../../types/theme';

interface GroupedBarChartProps {
  categories: (string | number)[];
  series: { name: string; values: (number | null)[] }[];
  title?: string;
  xlabel?: string;
  ylabel?: string;
  height?: number;
  barmode?: 'group' | 'stack' | 'relative';
  layout?: Partial<Layout>;
}

export default function GroupedBarChart({
  categories, series, title, xlabel, ylabel,
  height = 400, barmode = 'group', layout: extraLayout,
}: GroupedBarChartProps) {
  const data: Data[] = series.map((s, i) => ({
    type: 'bar',
    x: categories,
    y: s.values,
    name: s.name,
    marker: { color: CATEGORICAL_COLORS[i % CATEGORICAL_COLORS.length] },
    hovertemplate: '<b>%{x}</b><br>' + s.name + ': %{y:,.1f}<extra></extra>',
  }));

  const layout: Partial<Layout> = {
    title: title ? { text: title, x: 0.5 } : undefined,
    xaxis: { title: { text: xlabel }, tickangle: -45 },
    yaxis: { title: { text: ylabel } },
    barmode,
    showlegend: true,
    legend: { orientation: 'h', y: -0.28 },
    ...extraLayout,
  };

  return <BaseChart data={data} layout={layout} height={height} />;
}
