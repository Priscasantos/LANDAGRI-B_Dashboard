import { useMemo } from 'react';
import BaseChart from '../../charts/BaseChart';
import type { Data } from 'plotly.js';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { CATEGORICAL_COLORS } from '../../../types/theme';
import { useT } from '../../../i18n/LanguageContext';

interface AnnualCoverageTabProps {
  selectedInitiatives: string[];
}

export default function AnnualCoverageTab({ selectedInitiatives }: AnnualCoverageTabProps) {
  const { t } = useT('charts');
  const { t: tBody } = useT('initiative');
  const initiatives = useDashboardStore((s) => s.initiatives);

  const { bars, allYears } = useMemo(() => {
    const filtered = initiatives
      .filter((i) => selectedInitiatives.includes(i.Name))
      .filter((i) => i.Available_Years.length > 0);

    if (filtered.length === 0) {
      return { bars: [], allYears: [] };
    }

    const allYrs = new Set<number>();
    filtered.forEach((i) => i.Available_Years.forEach((y) => allYrs.add(y)));
    const sortedYears = [...allYrs].sort((a, b) => a - b);

    const b = filtered.map((i, idx) => {
      const color = CATEGORICAL_COLORS[idx % CATEGORICAL_COLORS.length];
      const sortedYrs = [...i.Available_Years].sort((a, b) => a - b);
      return {
        name: i.Display_Name,
        start: sortedYrs[0],
        end: sortedYrs[sortedYrs.length - 1],
        color,
      };
    });

    return { bars: b, allYears: sortedYears };
  }, [initiatives, selectedInitiatives]);

  if (bars.length === 0) {
    return (
      <div className="py-8 text-center text-fg-muted">
        {tBody('noSelectionAnnual')}
      </div>
    );
  }

  const trace: Data = {
    y: bars.map((b) => b.name),
    x: bars.map((b) => b.end - b.start),
    base: bars.map((b) => b.start),
    type: 'bar',
    orientation: 'h',
    marker: {
      color: bars.map((b) => b.color),
      line: { width: 1, color: 'white' },
    },
    text: bars.map((b) => `${b.start}–${b.end}`),
    textposition: 'inside',
    insidetextanchor: 'middle',
    hovertemplate: `<b>%{y}</b><br>${t('period')}: %{base} – %{base}+%{x}<extra></extra>`,
  };

  const yearRange = allYears.length > 0
    ? [Math.min(...allYears) - 1, Math.max(...allYears) + 1]
    : [2000, 2025];

  return (
    <div className="space-y-4">
      <p className="text-sm text-fg-secondary">
        {tBody('annualIntro')}
      </p>
      <BaseChart
        data={[trace]}
        layout={{
          title: { text: t('annualCoverageTimeline'), x: 0 },
          xaxis: {
            title: t('year'),
            range: yearRange,
            dtick: yearRange[1] - yearRange[0] > 40 ? 5 : 1,
          },
          yaxis: { title: '', autorange: 'reversed' },
          barmode: 'overlay',
          height: Math.max(300, bars.length * 50),
          margin: { l: 150, r: 30, t: 40, b: 60 },
        }}
      />
    </div>
  );
}
