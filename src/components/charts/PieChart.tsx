import BaseChart from './BaseChart';
import type { Data, Layout } from 'plotly.js';
import { CATEGORICAL_COLORS } from '../../types/theme';

interface PieSlice {
  label: string;
  value: number;
  color?: string;
}

interface PieChartProps {
  data: PieSlice[];
  title?: string;
  height?: number;
  donut?: boolean;
  showPercent?: boolean;
  layout?: Partial<Layout>;
}

export default function PieChart({
  data: slices, title, height = 400,
  donut = false, showPercent = true, layout: extraLayout,
}: PieChartProps) {
  const plotData: Data[] = [{
    type: 'pie',
    labels: slices.map(s => s.label),
    values: slices.map(s => s.value),
    marker: {
      colors: slices.map((s, i) => s.color || CATEGORICAL_COLORS[i % CATEGORICAL_COLORS.length]),
      line: { color: '#fff', width: 2 },
    },
    hole: donut ? 0.4 : 0,
    textinfo: showPercent ? 'label+percent' : 'label+value',
    textposition: 'outside',
    hovertemplate: '<b>%{label}</b><br>%{value:,.1f} (%{percent})<extra></extra>',
    automargin: true,
  }];

  const layout: Partial<Layout> = {
    title: title ? { text: title, x: 0.5 } : undefined,
    showlegend: true,
    legend: { orientation: 'h', y: -0.28 },
    ...extraLayout,
  };

  return <BaseChart data={plotData} layout={layout} height={height} />;
}
