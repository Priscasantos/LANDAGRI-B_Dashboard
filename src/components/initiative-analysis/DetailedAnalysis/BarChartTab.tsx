import { useState, useMemo } from 'react';
import BaseChart from '../../charts/BaseChart';
import type { Data } from 'plotly.js';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { CATEGORICAL_COLORS } from '../../../types/theme';
import { useT } from '../../../i18n/LanguageContext';
import Select from '../../ui/Select';

interface BarChartTabProps {
  selectedInitiatives: string[];
}

export default function BarChartTab({ selectedInitiatives }: BarChartTabProps) {
  const { t } = useT('charts');
  const { t: tBody } = useT('initiative');
  const initiatives = useDashboardStore((s) => s.initiatives);

  const [metric1, setMetric1] = useState('accuracy');
  const [metric2, setMetric2] = useState('resolution');
  const [metric3, setMetric3] = useState('classes');

  const metricOptions = [
    { value: 'accuracy', label: t('overallAccuracy') },
    { value: 'resolution', label: t('spatialResolution') },
    { value: 'classes', label: t('numberOfClasses') },
    { value: 'agriClasses', label: t('agricultureClasses') },
    { value: 'years', label: t('availableYears') },
  ];

  const getMetricValue = (initiative: typeof initiatives[0], metric: string): number => {
    switch (metric) {
      case 'accuracy': return initiative.Accuracy;
      case 'resolution': return initiative.Resolution;
      case 'classes': return initiative.Number_of_Classes;
      case 'agriClasses': return initiative.Number_of_Agriculture_Classes;
      case 'years': return initiative.Available_Years.length;
      default: return 0;
    }
  };

  const filteredData = useMemo(() => {
    return initiatives
      .filter((i) => selectedInitiatives.includes(i.Name))
      .map((i) => ({
        name: i.Display_Name,
        metric1: getMetricValue(i, metric1),
        metric2: getMetricValue(i, metric2),
        metric3: getMetricValue(i, metric3),
      }));
  }, [initiatives, selectedInitiatives, metric1, metric2, metric3]);

  if (filteredData.length === 0) {
    return (
      <div className="py-8 text-center text-fg-muted">
        {tBody('noSelectionMulti')}
      </div>
    );
  }

  const selectedMetrics = [metric1, metric2, metric3];
  const metricLabels = [metric1, metric2, metric3].map(
    (m) => metricOptions.find((o) => o.value === m)?.label || m,
  );

  const traces: Data[] = selectedMetrics.map((metric, idx) => ({
    name: metricLabels[idx],
    x: filteredData.map((d) => d.name),
    y: filteredData.map((d) => {
      switch (metric) {
        case 'accuracy': return d.metric1;
        case 'resolution': return d.metric2;
        case 'classes': return d.metric3;
        case 'agriClasses': return d.metric3; // fallback
        case 'years': return d.metric3; // fallback
        default: return 0;
      }
    }),
    type: 'bar',
    marker: { color: CATEGORICAL_COLORS[idx % CATEGORICAL_COLORS.length] },
    hovertemplate: `<b>%{x}</b><br>${metricLabels[idx]}: %{y}<extra></extra>`,
  }));

  return (
    <div className="space-y-4">
      <p className="text-sm text-fg-secondary">
        {tBody('barIntro')}
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Select
          label={tBody('metric1')}
          options={metricOptions}
          value={metric1}
          onChange={setMetric1}
        />
        <Select
          label={tBody('metric2')}
          options={metricOptions}
          value={metric2}
          onChange={setMetric2}
        />
        <Select
          label={tBody('metric3')}
          options={metricOptions}
          value={metric3}
          onChange={setMetric3}
        />
      </div>

      <BaseChart
        data={traces}
        layout={{
          title: { text: t('multiMetricComparison'), x: 0 },
          xaxis: { title: '' },
          yaxis: { title: t('value') },
          barmode: 'group',
          height: 450,
          margin: { l: 60, r: 20, t: 40, b: 120 },
        }}
      />
    </div>
  );
}
