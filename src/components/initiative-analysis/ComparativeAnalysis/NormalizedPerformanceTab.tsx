import { useMemo } from 'react';
import BaseChart from '../../charts/BaseChart';
import type { Data } from 'plotly.js';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { CATEGORICAL_COLORS } from '../../../types/theme';
import { minMaxNormalize } from '../../../lib/normalize';
import { hoverTemplatesForLocale } from '../../../lib/chartDefaults';
import { useT } from '../../../i18n/LanguageContext';

export default function NormalizedPerformanceTab() {
  const { t, locale } = useT('charts');
  const { t: tBody } = useT('initiative');
  const initiatives = useDashboardStore((s) => s.initiatives);

  const { heatmapData, metricLabels, initiativeLabels, metricComparison, radarData } = useMemo(() => {
    const valid = initiatives.filter(
      (i) => i.Accuracy > 0 && i.Resolution > 0 && i.Number_of_Classes > 0,
    );

    if (valid.length === 0) {
      return { heatmapData: [], metricLabels: [], initiativeLabels: [], metricComparison: [], radarData: [] };
    }

    const names = valid.map((i) => i.Display_Name);
    const metrics = [t('accuracyLabel'), t('resolutionInv'), t('totalClasses'), t('agricultureClasses')];

    // Build raw matrix [initiatives][metrics]
    const rawMatrix = valid.map((i) => [
      i.Accuracy,
      i.Resolution > 0 ? 1 / i.Resolution : 0,
      i.Number_of_Classes,
      i.Number_of_Agriculture_Classes,
    ]);

    // Normalize each metric column
    const normalizedMatrix = metrics.map((_, colIdx) => {
      const col = rawMatrix.map((row) => row[colIdx]);
      return minMaxNormalize(col);
    });

    // Transpose back
    const heatZ = valid.map((_, rowIdx) => metrics.map((_, colIdx) => normalizedMatrix[colIdx][rowIdx]));

    // Metric comparison (avg normalized)
    const metricComparison = metrics.map((label, idx) => ({
      label,
      avg: normalizedMatrix[idx].reduce((s, v) => s + v, 0) / normalizedMatrix[idx].length,
    }));

    // Radar data (first 5 initiatives)
    const radarInitiative = valid.slice(0, 5);
    const radarData = radarInitiative.map((i, idx) => ({
      name: i.Display_Name,
      r: [
        i.Accuracy,
        i.Resolution > 0 ? 1 / i.Resolution : 0,
        i.Number_of_Classes,
        i.Number_of_Agriculture_Classes,
      ].map((v, vi) => {
        const col = rawMatrix.map((row) => row[vi]);
        const min = Math.min(...col);
        const max = Math.max(...col);
        return max > min ? (v - min) / (max - min) : 0.5;
      }),
      color: CATEGORICAL_COLORS[idx % CATEGORICAL_COLORS.length],
    }));

    return {
      heatmapData: heatZ,
      metricLabels: metrics,
      initiativeLabels: names,
      metricComparison,
      radarData,
    };
  }, [initiatives, t]);

  if (heatmapData.length === 0) {
    return <div className="py-8 text-center text-fg-muted">{tBody('noNormalizedData')}</div>;
  }

  // Heatmap
  const heatTrace: Data = {
    z: heatmapData,
    x: metricLabels,
    y: initiativeLabels,
    type: 'heatmap',
    colorscale: 'Viridis',
    zmin: 0,
    zmax: 1,
    hovertemplate: '<b>%{y}</b><br>%{x}: %{z:.2f}<extra></extra>',
  };

  // Metric comparison bar
  const metricBar: Data = {
    x: metricComparison.map((d) => d.label),
    y: metricComparison.map((d) => d.avg),
    type: 'bar',
    marker: {
      color: metricComparison.map((_, i) => CATEGORICAL_COLORS[i % CATEGORICAL_COLORS.length]),
    },
    text: metricComparison.map((d) => d.avg.toFixed(2)),
    textposition: 'outside',
    hovertemplate: `<b>%{x}</b><br>${t('avgNormalized')}: %{y:.2f}<extra></extra>`,
  };

  // Radar
  const radarTraces: Data[] = radarData.map((d) => ({
    name: d.name,
    r: d.r,
    theta: metricLabels,
    type: 'scatterpolar',
    fill: 'toself',
    fillcolor: `${d.color}44`,
    line: { color: d.color, width: 2 },
    marker: { color: d.color, size: 6 },
    hovertemplate: hoverTemplatesForLocale(locale).radar,
  }));

  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-base font-semibold text-fg mb-2">{tBody('hNormalizedHeatmap')}</h3>
        <p className="text-sm text-fg-secondary mb-3">
          {tBody('normalizedIntro')}
        </p>
        <BaseChart
          data={[heatTrace]}
          layout={{
            title: { text: t('normalizedMetricsHeatmap'), x: 0 },
            xaxis: { title: '' },
            yaxis: { title: '', autorange: 'reversed' },
            height: Math.max(400, initiativeLabels.length * 25),
            margin: { l: 150, r: 20, t: 40, b: 80 },
          }}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-base font-semibold text-fg mb-2">{tBody('hAvgNormalized')}</h3>
          <BaseChart
            data={[metricBar]}
            layout={{
              title: { text: t('avgNormalizedScoreByMetric'), x: 0 },
              xaxis: { title: '' },
              yaxis: { title: t('avg01') },
              height: 350,
            }}
          />
        </div>
        <div>
          <h3 className="text-base font-semibold text-fg mb-2">{tBody('hRadarTop5')}</h3>
          <BaseChart
            data={radarTraces}
            layout={{
              title: { text: t('multiMetricRadar'), x: 0 },
              height: 400,
              polar: {
                radialaxis: { visible: true, range: [0, 1] },
              },
            }}
          />
        </div>
      </div>
    </div>
  );
}
