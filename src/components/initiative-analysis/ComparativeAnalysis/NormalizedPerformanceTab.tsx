import { useMemo } from 'react';
import EChartsHeatmap from '../../charts/echarts/EChartsHeatmap';
import EChartsGroupedBar from '../../charts/echarts/EChartsGroupedBar';
import EChartsRadar from '../../charts/echarts/EChartsRadar';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { CATEGORICAL_COLORS } from '../../../types/theme';
import { minMaxNormalize } from '../../../lib/normalize';
import { useT } from '../../../i18n/LanguageContext';

/**
 * Normalized performance (heatmap + avg bars + top-5 radar) — ECharts
 * edition (Fase 2 fatia 2c). Replaces the Plotly `BaseChart` heatmap/bar/
 * `scatterpolar`; min-max normalization, i18n and chrome unchanged.
 * Reversible: previous version in git history.
 */
export default function NormalizedPerformanceTab() {
  const { t } = useT('charts');
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
      values: [
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

  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-base font-semibold text-fg mb-2">{tBody('hNormalizedHeatmap')}</h3>
        <p className="text-sm text-fg-secondary mb-3">
          {tBody('normalizedIntro')}
        </p>
        <EChartsHeatmap
          z={heatmapData}
          x={metricLabels}
          y={initiativeLabels}
          captionKey="normalizedMetricsHeatmap"
          height={Math.max(400, initiativeLabels.length * 25)}
          colors={['#440154', '#3b528b', '#21918c', '#5ec962', '#fde725']}
          min={0}
          max={1}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-base font-semibold text-fg mb-2">{tBody('hAvgNormalized')}</h3>
          <EChartsGroupedBar
            categories={metricComparison.map((d) => d.label)}
            series={[{ name: t('avg01'), values: metricComparison.map((d) => d.avg) }]}
            captionKey="avgNormalizedScoreByMetric"
            height={350}
          />
        </div>
        <div>
          <h3 className="text-base font-semibold text-fg mb-2">{tBody('hRadarTop5')}</h3>
          <EChartsRadar
            indicators={metricLabels}
            series={radarData}
            captionKey="multiMetricRadar"
            height={400}
          />
        </div>
      </div>
    </div>
  );
}
