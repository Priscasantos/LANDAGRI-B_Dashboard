import { useMemo } from 'react';
import BaseChart from '../../charts/BaseChart';
import type { Data } from 'plotly.js';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { CATEGORICAL_COLORS } from '../../../types/theme';
import { minMaxNormalize } from '../../../lib/normalize';
import { hoverTemplatesForLocale } from '../../../lib/chartDefaults';
import { translate } from '../../../i18n/index';
import { useT } from '../../../i18n/LanguageContext';

interface RadarTabProps {
  selectedInitiatives: string[];
}

export default function RadarTab({ selectedInitiatives }: RadarTabProps) {
  const { t, locale } = useT('charts');
  const { t: tBody } = useT('initiative');
  const initiatives = useDashboardStore((s) => s.initiatives);

  const { traces } = useMemo(() => {
    // `translate(locale, …)` direto (em vez do `t` do hook): o memo
    // depende só de `locale`, sem aviso de dep desnecessária no lint.
    const thetaLabels = [translate(locale, 'charts', 'overallAccuracyLabel'), translate(locale, 'charts', 'spatialResolutionLabel'), translate(locale, 'charts', 'totalClasses'), translate(locale, 'charts', 'agricultureClasses')];
    const filtered = initiatives
      .filter((i) => selectedInitiatives.includes(i.Name))
      .filter((i) => i.Accuracy > 0 && i.Resolution > 0);

    if (filtered.length === 0) {
      return { traces: [], theta: thetaLabels };
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

    const t = filtered.map((i, idx) => ({
      name: i.Display_Name,
      r: [normAccuracy[idx], normResolution[idx], normClasses[idx], normAgriClasses[idx]],
      color: CATEGORICAL_COLORS[idx % CATEGORICAL_COLORS.length],
    }));

    const traces: Data[] = t.map((d) => ({
      name: d.name,
      r: d.r,
      theta: thetaLabels,
      type: 'scatterpolar',
      fill: 'toself',
      fillcolor: `${d.color}44`,
      line: { color: d.color, width: 2 },
      marker: { color: d.color, size: 5 },
      hovertemplate: hoverTemplatesForLocale(locale).radar,
    }));

    return { traces, theta: thetaLabels };
  }, [initiatives, selectedInitiatives, locale]);

  if (traces.length === 0) {
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
      <BaseChart
        data={traces}
        layout={{
          title: { text: t('multiMetricRadar'), x: 0 },
          height: 500,
          polar: {
            radialaxis: {
              visible: true,
              range: [0, 1],
              tickvals: [0, 0.25, 0.5, 0.75, 1],
            },
          },
          legend: {
            orientation: 'h',
            y: -0.28,
          },
        }}
      />
    </div>
  );
}
