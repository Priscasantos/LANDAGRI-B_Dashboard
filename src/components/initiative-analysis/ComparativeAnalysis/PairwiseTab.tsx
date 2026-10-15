import { useMemo } from 'react';
import EChartsScatter from '../../charts/echarts/EChartsScatter';
import type { ScatterSeriesInput } from '../../charts/echarts/echarts-options';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { CATEGORICAL_COLORS } from '../../../types/theme';
import { useT } from '../../../i18n/LanguageContext';

/**
 * Accuracy vs resolution bubble chart — ECharts edition (Fase 2 fatia 2c).
 * Replaces the Plotly `BaseChart` bubble scatter (log resolution axis,
 * bubble size = class count, initiative labels); store filter, i18n and
 * chrome unchanged. Reversible: previous version in git history.
 */
export default function PairwiseTab() {
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

  const series: ScatterSeriesInput[] = useMemo(
    () =>
      chartData.map((d, i) => ({
        name: d.name,
        data: [[d.accuracy, d.resolution]],
        color: CATEGORICAL_COLORS[i % CATEGORICAL_COLORS.length],
        sizes: [d.classes],
        labels: [d.name],
      })),
    [chartData],
  );

  if (chartData.length === 0) {
    return <div className="py-8 text-center text-fg-muted">{tBody('noPairwiseData')}</div>;
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-fg-secondary">
        {tBody('pairwiseIntro')}
      </p>
      <EChartsScatter
        series={series}
        captionKey="accuracyVsResolution"
        height={500}
        yAxisType="log"
      />
    </div>
  );
}
