import { useMemo } from 'react';
import EChartsGroupedBar from '../../charts/echarts/EChartsGroupedBar';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { CATEGORICAL_COLORS } from '../../../types/theme';
import { useT } from '../../../i18n/LanguageContext';

/**
 * Methodology × coverage grouped bars — ECharts edition (Fase 2 fatia 2c).
 * Replaces the Plotly `BaseChart` grouped bar; grouping, i18n and chrome
 * unchanged. Reversible: previous version in git history.
 */
export default function MethodologyDistributionTab() {
  const { t: tBody } = useT('initiative');
  const initiatives = useDashboardStore((s) => s.initiatives);

  const { methods, coverageTypes, groupedData } = useMemo(() => {
    const methods = [...new Set(initiatives.map((i) => i.Methodology))].sort();
    const coverages = [...new Set(initiatives.map((i) => i.Coverage))].sort();

    const grouped: Record<string, Record<string, number>> = {};
    methods.forEach((m) => {
      grouped[m] = {};
      coverages.forEach((c) => {
        grouped[m][c] = 0;
      });
    });

    initiatives.forEach((i) => {
      if (grouped[i.Methodology] && grouped[i.Methodology][i.Coverage] !== undefined) {
        grouped[i.Methodology][i.Coverage]++;
      }
    });

    return { methods, coverageTypes: coverages, groupedData: grouped };
  }, [initiatives]);

  if (methods.length === 0) {
    return <div className="py-8 text-center text-fg-muted">{tBody('noMethodologyData')}</div>;
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-fg-secondary">
        {tBody('methodologyDistIntro')}
      </p>
      <EChartsGroupedBar
        categories={methods}
        series={coverageTypes.map((cov, idx) => ({
          name: cov,
          values: methods.map((m) => groupedData[m]?.[cov] || 0),
          color: CATEGORICAL_COLORS[idx % CATEGORICAL_COLORS.length],
        }))}
        captionKey="methodologyCoverageDistribution"
        height={400}
      />
    </div>
  );
}
