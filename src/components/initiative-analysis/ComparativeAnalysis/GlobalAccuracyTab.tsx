import { useMemo } from 'react';
import BaseChart from '../../charts/BaseChart';
import type { Data } from 'plotly.js';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { CATEGORICAL_COLORS } from '../../../types/theme';
import { useT } from '../../../i18n/LanguageContext';

export default function GlobalAccuracyTab() {
  const { t } = useT('charts');
  const { t: tBody } = useT('initiative');
  const initiatives = useDashboardStore((s) => s.initiatives);

  const chartData = useMemo(() => {
    return initiatives
      .filter((i) => i.Accuracy > 0)
      .map((i) => ({
        name: i.Display_Name,
        accuracy: i.Accuracy,
        accuracyMin: i.Accuracy_Min,
        accuracyMax: i.Accuracy_Max,
      }))
      .sort((a, b) => b.accuracy - a.accuracy);
  }, [initiatives]);

  if (chartData.length === 0) {
    return <div className="py-8 text-center text-fg-muted">{tBody('noAccuracyData')}</div>;
  }

  const barTrace: Data = {
    x: chartData.map((d) => d.name),
    y: chartData.map((d) => d.accuracy),
    type: 'bar',
    marker: {
      color: chartData.map(
        (d, i) => CATEGORICAL_COLORS[i % CATEGORICAL_COLORS.length],
      ),
    },
    text: chartData.map((d) => `${d.accuracy}%`),
    textposition: 'outside',
    hovertemplate:
      `<b>%{x}</b><br>${t('accuracyLabel')}: %{y:.1f}%<br>${t('range')}: [%{customdata[0]:.1f}% – %{customdata[1]:.1f}%]<extra></extra>`,
    customdata: chartData.map((d) => [d.accuracyMin || 0, d.accuracyMax || 0]),
  };

  const avgAccuracy =
    chartData.reduce((s, d) => s + d.accuracy, 0) / chartData.length;

  const avgTrace: Data = {
    x: [chartData[0]?.name || '', chartData[chartData.length - 1]?.name || ''],
    y: [avgAccuracy, avgAccuracy],
    type: 'scatter',
    mode: 'lines',
    name: `${t('average')} (${avgAccuracy.toFixed(1)}%)`,
    line: { color: '#ef4444', width: 2, dash: 'dash' },
    hoverinfo: 'skip',
  };

  return (
    <div className="space-y-4">
      <p className="text-sm text-fg-secondary">
        {tBody('accuracyIntro')}
      </p>
      <BaseChart
        data={[barTrace, avgTrace]}
        layout={{
          title: { text: t('overallAccuracyByInitiative'), x: 0 },
          xaxis: { title: '' },
          yaxis: { title: t('overallAccuracyPct'), range: [0, 105] },
          height: 450,
          margin: { l: 50, r: 20, t: 40, b: 120 },
          shapes: [
            {
              type: 'line',
              xref: 'paper',
              x0: 0,
              x1: 1,
              y0: avgAccuracy,
              y1: avgAccuracy,
              line: { color: '#ef4444', width: 2, dash: 'dash' },
            },
          ],
        }}
      />

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="bg-surface rounded-lg border border-border p-3 text-center">
          <div className="text-xs text-fg-secondary">{tBody('cardAvgAccuracy')}</div>
          <div className="text-lg font-bold text-emerald-600">{avgAccuracy.toFixed(1)}%</div>
        </div>
        <div className="bg-surface rounded-lg border border-border p-3 text-center">
          <div className="text-xs text-fg-secondary">{tBody('cardHighestAccuracy')}</div>
          <div className="text-lg font-bold text-blue-600">
            {Math.max(...chartData.map((d) => d.accuracy)).toFixed(1)}%
          </div>
        </div>
        <div className="bg-surface rounded-lg border border-border p-3 text-center">
          <div className="text-xs text-fg-secondary">{tBody('cardLowestAccuracy')}</div>
          <div className="text-lg font-bold text-orange-600">
            {Math.min(...chartData.map((d) => d.accuracy)).toFixed(1)}%
          </div>
        </div>
      </div>
    </div>
  );
}
