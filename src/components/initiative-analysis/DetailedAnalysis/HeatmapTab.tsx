import { useMemo } from 'react';
import EChartsHeatmap from '../../charts/echarts/EChartsHeatmap';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { useT } from '../../../i18n/LanguageContext';

interface HeatmapTabProps {
  selectedInitiatives: string[];
}

/**
 * Metric correlation matrix — ECharts edition (Fase 2 fatia 2c).
 * Replaces the Plotly `BaseChart` heatmap (diverging −1…1 scale with cell
 * values); Pearson computation, i18n and chrome unchanged.
 * Reversible: previous version in git history.
 */
export default function HeatmapTab({ selectedInitiatives }: HeatmapTabProps) {
  const { t } = useT('charts');
  const { t: tBody } = useT('initiative');
  const initiatives = useDashboardStore((s) => s.initiatives);

  const { zMatrix, metricLabels, selectionSize } = useMemo(() => {
    const filtered = initiatives
      .filter((i) => selectedInitiatives.includes(i.Name))
      .filter((i) => i.Accuracy > 0 && i.Resolution > 0);

    if (filtered.length === 0) {
      return { zMatrix: [], metricLabels: [], selectionSize: 0 };
    }

    const metrics = [t('overallAccuracyPct'), t('spatialResolution'), t('numberOfClasses'), t('agricultureClasses'), t('availableYears')];
    const metricGetters: ((i: typeof filtered[0]) => number)[] = [
      (i) => i.Accuracy,
      (i) => i.Resolution,
      (i) => i.Number_of_Classes,
      (i) => i.Number_of_Agriculture_Classes,
      (i) => i.Available_Years.length,
    ];

    const z = filtered.map((item) => metricGetters.map((getter) => getter(item)));

    return { zMatrix: z, metricLabels: metrics, selectionSize: filtered.length };
  }, [initiatives, selectedInitiatives, t]);

  // Compute correlation matrix between metrics (must be before conditional return for React hooks)
  const correlationMatrix = useMemo(() => {
    const numMetrics = metricLabels.length;
    const numInitiatives = zMatrix.length;

    if (numInitiatives < 2) {
      // Can't compute correlation with < 2 data points
      return Array.from({ length: numMetrics }, () =>
        Array.from({ length: numMetrics }, () => 0),
      );
    }

    const correlation = Array.from({ length: numMetrics }, () =>
      Array.from({ length: numMetrics }, () => 0),
    );

    for (let i = 0; i < numMetrics; i++) {
      for (let j = 0; j < numMetrics; j++) {
        const xi = zMatrix.map((row) => row[i]);
        const yj = zMatrix.map((row) => row[j]);

        const meanX = xi.reduce((s, v) => s + v, 0) / xi.length;
        const meanY = yj.reduce((s, v) => s + v, 0) / yj.length;

        let numerator = 0;
        let denomX = 0;
        let denomY = 0;

        for (let k = 0; k < xi.length; k++) {
          const dx = xi[k] - meanX;
          const dy = yj[k] - meanY;
          numerator += dx * dy;
          denomX += dx * dx;
          denomY += dy * dy;
        }

        const denom = Math.sqrt(denomX * denomY);
        correlation[i][j] = denom > 0 ? numerator / denom : 0;
      }
    }

    return correlation;
  }, [zMatrix, metricLabels]);

  return (
    <div className="space-y-4">
      <p className="text-sm text-fg-secondary">
        {tBody('heatmapIntro')}
      </p>

      {selectionSize < 2 && (
        <div className="bg-amber-50 border border-amber-200 text-amber-700 px-4 py-2 rounded text-sm">
          {tBody('needTwo')}
        </div>
      )}

      <EChartsHeatmap
        z={correlationMatrix}
        x={metricLabels}
        y={metricLabels}
        captionKey="metricCorrelationMatrix"
        height={450}
        colors={['#2166ac', '#f7f7f7', '#b2182b']}
        min={-1}
        max={1}
        showValues
        labelDarkRange={[-0.35, 0.35]}
      />
    </div>
  );
}
