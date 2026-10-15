import { useMemo } from 'react';
import BaseChart from '../../charts/BaseChart';
import type { Data } from 'plotly.js';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { CATEGORICAL_COLORS } from '../../../types/theme';
import { useT } from '../../../i18n/LanguageContext';

export default function PairwiseTab() {
  const { t } = useT('charts');
  const { t: tBody } = useT('initiative');
  const initiatives = useDashboardStore((s) => s.initiatives);

  const chartData = useMemo(() => {
    const valid = initiatives.filter(
      (i) => i.Accuracy > 0 && i.Resolution > 0 && i.Number_of_Classes > 0,
    );
    return valid.map((i) => ({
      name: i.Display_Name,
      accuracy: i.Accuracy,
      resolution: i.Resolution,
      classes: i.Number_of_Classes,
      coverage: i.Coverage,
      methodology: i.Methodology,
    }));
  }, [initiatives]);

  if (chartData.length === 0) {
    return <div className="py-8 text-center text-fg-muted">{tBody('noPairwiseData')}</div>;
  }

  const scatterTrace: Data = {
    x: chartData.map((d) => d.accuracy),
    y: chartData.map((d) => d.resolution),
    text: chartData.map((d) => d.name),
    type: 'scatter',
    mode: 'markers+text',
    marker: {
      size: chartData.map((d) => Math.max(8, Math.min(20, d.classes))),
      color: chartData.map((d, i) => CATEGORICAL_COLORS[i % CATEGORICAL_COLORS.length]),
      line: { width: 2, color: 'white' },
      opacity: 0.85,
    },
    textposition: 'top center',
    textfont: { size: 9 },
    hovertemplate:
      `<b>%{text}</b><br>${t('accuracyLabel')}: %{x:.1f}%<br>${t('resolutionLabel')}: %{y}m<br>${t('classes')}: %{customdata}<extra></extra>`,
    customdata: chartData.map((d) => d.classes),
  };

  return (
    <div className="space-y-4">
      <p className="text-sm text-fg-secondary">
        {tBody('pairwiseIntro')}
      </p>
      <BaseChart
        data={[scatterTrace]}
        layout={{
          title: { text: t('accuracyVsResolution'), x: 0 },
          xaxis: { title: t('overallAccuracyPct'), range: [50, 105] },
          yaxis: { title: t('spatialResolution'), type: 'log' },
          height: 500,
          hovermode: 'closest',
        }}
      />
    </div>
  );
}
