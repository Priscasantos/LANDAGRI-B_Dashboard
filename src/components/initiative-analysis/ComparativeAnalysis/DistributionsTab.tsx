import { useMemo } from 'react';
import BaseChart from '../../charts/BaseChart';
import type { Data } from 'plotly.js';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { CATEGORICAL_COLORS } from '../../../types/theme';
import { useT } from '../../../i18n/LanguageContext';

export default function DistributionsTab() {
  const { t } = useT('charts');
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
        name: i.Display_Name,
        resolution: i.Resolution,
      }))
      .sort((a, b) => a.resolution - b.resolution);

    const tempBars = initiatives
      .filter((i) => i.Available_Years.length > 0)
      .map((i) => ({
        name: i.Display_Name,
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
  }, [initiatives]);

  if (initiatives.length === 0) {
    return <div className="py-8 text-center text-fg-muted">{tBody('noDistributionData')}</div>;
  }

  // Methodology pie
  const pieTrace: Data = {
    labels: methodologyCounts.map((d) => d.method),
    values: methodologyCounts.map((d) => d.count),
    type: 'pie',
    marker: { colors: CATEGORICAL_COLORS.slice(0, methodologyCounts.length) },
    textinfo: 'label+percent',
    hovertemplate: `<b>%{label}</b><br>${t('count')}: %{value}<extra></extra>`,
  };

  // Resolution bars
  const resTrace: Data = {
    x: resolutionBars.map((d) => d.name),
    y: resolutionBars.map((d) => d.resolution),
    type: 'bar',
    marker: {
      color: resolutionBars.map(
        (_, i) => CATEGORICAL_COLORS[i % CATEGORICAL_COLORS.length],
      ),
    },
    text: resolutionBars.map((d) => `${d.resolution}m`),
    textposition: 'outside',
    hovertemplate: `<b>%{x}</b><br>${t('resolutionLabel')}: %{y}m<extra></extra>`,
  };

  // Temporal coverage horizontal bars
  const tempTrace: Data = {
    y: tempCoverageBars.map((d) => d.name),
    x: tempCoverageBars.map((d) => d.duration),
    type: 'bar',
    orientation: 'h',
    marker: {
      color: tempCoverageBars.map(
        (_, i) => CATEGORICAL_COLORS[i % CATEGORICAL_COLORS.length],
      ),
    },
    text: tempCoverageBars.map((d) => `${d.duration}y`),
    textposition: 'outside',
    hovertemplate: `<b>%{y}</b><br>${t('duration')}: %{x} ${t('yearsUnitLong')}<extra></extra>`,
  };

  return (
    <div className="space-y-8">
      {/* Methodology Distribution Pie */}
      <div>
        <h3 className="text-base font-semibold text-fg mb-2">{tBody('hMethodologyDist')}</h3>
        <BaseChart
          data={[pieTrace]}
          layout={{
            title: { text: t('initiativesByMethodology'), x: 0 },
            height: 350,
          }}
        />
      </div>

      {/* Resolution Comparison */}
      <div>
        <h3 className="text-base font-semibold text-fg mb-2">{tBody('hSpatialRes')}</h3>
        <BaseChart
          data={[resTrace]}
          layout={{
            title: { text: t('spatialResolutionByInitiative'), x: 0 },
            xaxis: { title: '' },
            yaxis: { title: t('resolutionM'), type: 'log' },
            height: 400,
            margin: { l: 50, r: 20, t: 40, b: 120 },
          }}
        />
      </div>

      {/* Temporal Coverage */}
      <div>
        <h3 className="text-base font-semibold text-fg mb-2">{tBody('hTempDuration')}</h3>
        <BaseChart
          data={[tempTrace]}
          layout={{
            title: { text: t('temporalCoverageByInitiativeYears'), x: 0 },
            xaxis: { title: t('durationYears') },
            yaxis: { title: '', autorange: 'reversed' },
            height: Math.max(350, tempCoverageBars.length * 30),
            margin: { l: 150, r: 40, t: 40, b: 50 },
          }}
        />
      </div>
    </div>
  );
}
