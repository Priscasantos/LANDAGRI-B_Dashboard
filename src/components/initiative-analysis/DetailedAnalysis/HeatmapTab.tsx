import { useMemo } from 'react';
import BaseChart from '../../charts/BaseChart';
import type { Data } from 'plotly.js';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { useT } from '../../../i18n/LanguageContext';

interface HeatmapTabProps {
  selectedInitiatives: string[];
}

export default function HeatmapTab({ selectedInitiatives }: HeatmapTabProps) {
  const { t } = useT('charts');
  const { t: tBody } = useT('initiative');
  const initiatives = useDashboardStore((s) => s.initiatives);

  const { zMatrix, metricLabels } = useMemo(() => {
    const filtered = initiatives
      .filter((i) => selectedInitiatives.includes(i.Name))
      .filter((i) => i.Accuracy > 0 && i.Resolution > 0);

    if (filtered.length === 0) {
      return { zMatrix: [], metricLabels: [] };
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

    return { zMatrix: z, metricLabels: metrics };
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

  const heatTrace: Data = {
    z: correlationMatrix,
    x: metricLabels,
    y: metricLabels,
    type: 'heatmap',
    colorscale: 'Viridis',
    zmin: -1,
    zmax: 1,
    text: correlationMatrix.map((row) => row.map((v: number) => v.toFixed(2))),
    texttemplate: '%{text}',
    textfont: { size: 10, color: 'white' },
    hovertemplate: `<b>%{x}</b> vs <b>%{y}</b><br>${t('correlation')}: %{z:.2f}<extra></extra>`,
  };

  return (
    <div className="space-y-4">
      <p className="text-sm text-fg-secondary">
        {tBody('heatmapIntro')}
      </p>

      {zMatrix.length < 2 && (
        <div className="bg-amber-50 border border-amber-200 text-amber-700 px-4 py-2 rounded text-sm">
          {tBody('needTwo')}
        </div>
      )}

      <BaseChart
        data={[heatTrace]}
        layout={{
          title: { text: t('metricCorrelationMatrix'), x: 0 },
          xaxis: { title: '' },
          yaxis: { title: '' },
          height: 450,
          margin: { l: 120, b: 80 },
        }}
      />
    </div>
  );
}
