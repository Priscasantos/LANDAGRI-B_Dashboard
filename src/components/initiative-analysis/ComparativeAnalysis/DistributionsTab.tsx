import { useMemo } from 'react';
import EChartsPie from '../../charts/echarts/EChartsPie';
import EChartsGroupedBar from '../../charts/echarts/EChartsGroupedBar';
import EChartsHorizontalBar from '../../charts/echarts/EChartsHorizontalBar';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { getInitiativeShortName, translateMethodology } from '../../../data/glossary';
import { useT } from '../../../i18n/LanguageContext';

/**
 * Methodology / resolution / temporal distributions — ECharts edition
 * (Fase 2 fatia 2c). Replaces the three Plotly `BaseChart` charts
 * (pie + log-scale bar + horizontal duration bar); computations, i18n and
 * chrome unchanged. Reversible: previous version in git history.
 */
export default function DistributionsTab() {
  const { t, locale } = useT('charts');
  const { t: tBody } = useT('initiative');
  const initiatives = useDashboardStore((s) => s.initiatives);

  const { methodologyCounts, resolutionBars, tempCoverageBars } = useMemo(() => {
    const methodCount: Record<string, number> = {};
    initiatives.forEach((i) => {
      methodCount[i.Methodology] = (methodCount[i.Methodology] || 0) + 1;
    });

    const resBars = initiatives
      .filter((i) => i.Resolution > 0)
      .map((i) => ({
        name: getInitiativeShortName(i.Display_Name, locale),
        resolution: i.Resolution,
      }))
      .sort((a, b) => a.resolution - b.resolution);

    const tempBars = initiatives
      .filter((i) => i.Available_Years.length > 0)
      .map((i) => ({
        name: getInitiativeShortName(i.Display_Name, locale),
        start: i.Year_Start,
        end: i.Year_End,
        duration: i.Year_End - i.Year_Start + 1,
      }))
      .sort((a, b) => b.duration - a.duration);

    return {
      methodologyCounts: Object.entries(methodCount)
        .map(([method, count]) => ({ method, count }))
        .sort((a, b) => b.count - a.count),
      resolutionBars: resBars,
      tempCoverageBars: tempBars,
    };
  }, [initiatives, locale]);

  if (initiatives.length === 0) {
    return <div className="py-8 text-center text-fg-muted">{tBody('noDistributionData')}</div>;
  }

  return (
    <div className="space-y-8">
      {/* Methodology Distribution Pie */}
      <div>
        <h3 className="text-base font-semibold text-fg mb-2">{tBody('hMethodologyDist')}</h3>
        <EChartsPie
          data={methodologyCounts.map((d) => ({ label: translateMethodology(d.method, locale), value: d.count }))}
          captionKey="initiativesByMethodology"
          height={350}
          donut
        />
      </div>

      {/* Resolution Comparison */}
      <div>
        <h3 className="text-base font-semibold text-fg mb-2">{tBody('hSpatialRes')}</h3>
        <EChartsGroupedBar
          categories={resolutionBars.map((d) => d.name)}
          series={[{ name: t('resolutionM'), values: resolutionBars.map((d) => d.resolution) }]}
          captionKey="spatialResolutionByInitiative"
          height={400}
          yAxisType="log"
        />
      </div>

      {/* Temporal Coverage */}
      <div>
        <h3 className="text-base font-semibold text-fg mb-2">{tBody('hTempDuration')}</h3>
        <EChartsHorizontalBar
          labels={tempCoverageBars.map((d) => d.name)}
          values={tempCoverageBars.map((d) => d.duration)}
          captionKey="temporalCoverageByInitiativeYears"
          height={Math.max(350, tempCoverageBars.length * 30)}
        />
      </div>
    </div>
  );
}
