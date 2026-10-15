import { useState, useMemo } from 'react';
import EChartsGroupedBar from '../../charts/echarts/EChartsGroupedBar';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { CATEGORICAL_COLORS } from '../../../types/theme';
import { useT } from '../../../i18n/LanguageContext';
import Select from '../../ui/Select';

interface BarChartTabProps {
  selectedInitiatives: string[];
}

/**
 * Multi-metric grouped bars — ECharts edition (Fase 2 fatia 2c).
 * Replaces the Plotly `BaseChart` grouped bar; metric selectors, value
 * mapping, i18n and chrome unchanged.
 * Reversible: previous version in git history.
 */
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

  const filteredData = useMemo(() => {
    const getValue = (initiative: typeof initiatives[0], metric: string): number => {
      switch (metric) {
        case 'accuracy': return initiative.Accuracy;
        case 'resolution': return initiative.Resolution;
        case 'classes': return initiative.Number_of_Classes;
        case 'agriClasses': return initiative.Number_of_Agriculture_Classes;
        case 'years': return initiative.Available_Years.length;
        default: return 0;
      }
    };
    return initiatives
      .filter((i) => selectedInitiatives.includes(i.Name))
      .map((i) => ({
        name: i.Display_Name,
        metric1: getValue(i, metric1),
        metric2: getValue(i, metric2),
        metric3: getValue(i, metric3),
      }));
  }, [initiatives, selectedInitiatives, metric1, metric2, metric3]);

  if (filteredData.length === 0) {
    return (
      <div className="py-8 text-center text-fg-muted">
        {tBody('noSelectionMulti')}
      </div>
    );
  }

  const metricLabels = [metric1, metric2, metric3].map(
    (m) => metricOptions.find((o) => o.value === m)?.label || m,
  );
  const metricValues = [
    filteredData.map((d) => d.metric1),
    filteredData.map((d) => d.metric2),
    filteredData.map((d) => d.metric3),
  ];

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

      <EChartsGroupedBar
        categories={filteredData.map((d) => d.name)}
        series={metricLabels.map((label, idx) => ({
          name: label,
          values: metricValues[idx],
          color: CATEGORICAL_COLORS[idx % CATEGORICAL_COLORS.length],
        }))}
        captionKey="multiMetricComparison"
        height={450}
      />
    </div>
  );
}
