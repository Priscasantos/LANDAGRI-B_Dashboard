import BaseChart from './BaseChart';
import type { Data, Layout } from 'plotly.js';
import { CATEGORICAL_COLORS } from '../../types/theme';
import { useT } from '../../i18n/LanguageContext';

interface GanttBar {
  label: string;
  start: number;
  end: number;
  category?: string;
  color?: string;
}

interface GanttChartProps {
  bars: GanttBar[];
  title?: string;
  xlabel?: string;
  ylabel?: string;
  height?: number;
  layout?: Partial<Layout>;
}

export default function GanttChart({
  bars, title, xlabel, ylabel,
  height = 500, layout: extraLayout,
}: GanttChartProps) {
  // Período do hover no locale ativo (Fase 2); rótulos são dados (culturas).
  const { t } = useT('charts');
  const categories = [...new Set(bars.map(b => b.category || '').filter(Boolean))];
  const colorMap = new Map<string, string>();
  categories.forEach((cat, i) => {
    colorMap.set(cat, CATEGORICAL_COLORS[i % CATEGORICAL_COLORS.length]);
  });

  const data: Data[] = bars.map((bar) => ({
    type: 'bar',
    base: bar.start,
    x: [bar.end - bar.start],
    y: [bar.label],
    orientation: 'h',
    name: bar.category || bar.label,
    marker: {
      color: bar.color || colorMap.get(bar.category || '') || CATEGORICAL_COLORS[0],
      line: { color: '#fff', width: 1 },
    },
    hovertemplate: `<b>${bar.label}</b><br>${t('period')}: ${bar.start} - ${bar.end}<extra></extra>`,
    showlegend: false,
    width: 0.6,
  }));

  const layout: Partial<Layout> = {
    title: title ? { text: title, x: 0.5 } : undefined,
    xaxis: { title: xlabel || `${t('period')} (${t('month').toLowerCase()})` },
    yaxis: {
      title: { text: ylabel },
      automargin: true,
      categoryorder: 'array',
      categoryarray: bars.map(b => b.label).reverse(),
    },
    bargap: 0.3,
    barmode: 'stack',
    ...extraLayout,
  };

  return <BaseChart data={data} layout={layout} height={height} />;
}
