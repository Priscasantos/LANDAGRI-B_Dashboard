import { useMemo } from 'react';
import EChartsRadar from '../../charts/echarts/EChartsRadar';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { minMaxNormalize } from '../../../lib/normalize';
import { getInitiativeShortName } from '../../../data/glossary';
import { translate } from '../../../i18n/index';
import { useT } from '../../../i18n/LanguageContext';

interface RadarTabProps {
  selectedInitiatives: string[];
}

/**
 * Multi-metric radar — ECharts edition (Fase 2 fatia 2c).
 * Replaces the Plotly `scatterpolar`; min-max normalization, locale-reactive
 * indicators, i18n and chrome unchanged.
 * Reversible: previous version in git history.
 */
export default function RadarTab({ selectedInitiatives }: RadarTabProps) {
  const { locale } = useT('charts');
  const { t: tBody } = useT('initiative');
  const initiatives = useDashboardStore((s) => s.initiatives);

  const { indicators, radarSeries } = useMemo(() => {
    // `translate(locale, …)` direto (em vez do `t` do hook): o memo
    // depende só de `locale`, sem aviso de dep desnecessária no lint.
    const thetaLabels = [translate(locale, 'charts', 'overallAccuracyLabel'), translate(locale, 'charts', 'spatialResolutionLabel'), translate(locale, 'charts', 'totalClasses'), translate(locale, 'charts', 'agricultureClasses')];
    const filtered = initiatives
      .filter((i) => selectedInitiatives.includes(i.Name))
      .filter((i) => i.Accuracy > 0 && i.Resolution > 0);

    if (filtered.length === 0) {
      return { indicators: thetaLabels, radarSeries: [] };
    }

    // Extract raw values for normalization
    const rawAccuracy = filtered.map((i) => i.Accuracy);
    const rawResolution = filtered.map((i) => 1 / i.Resolution); // invert so higher = better
    const rawClasses = filtered.map((i) => i.Number_of_Classes);
    const rawAgriClasses = filtered.map((i) => i.Number_of_Agriculture_Classes);

    const normAccuracy = minMaxNormalize(rawAccuracy);
    const normResolution = minMaxNormalize(rawResolution);
    const normClasses = minMaxNormalize(rawClasses);
    const normAgriClasses = minMaxNormalize(rawAgriClasses);

    const series = filtered.map((i, idx) => ({
      name: getInitiativeShortName(i.Display_Name, locale),
      values: [normAccuracy[idx], normResolution[idx], normClasses[idx], normAgriClasses[idx]],
    }));

    return { indicators: thetaLabels, radarSeries: series };
  }, [initiatives, selectedInitiatives, locale]);

  if (radarSeries.length === 0) {
    return (
      <div className="py-8 text-center text-fg-muted">
        {tBody('noSelectionRadar')}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-fg-secondary">
        {tBody('radarIntro')}
      </p>
      <EChartsRadar
        indicators={indicators}
        series={radarSeries}
        captionKey="multiMetricRadar"
        height={500}
      />
    </div>
  );
}
