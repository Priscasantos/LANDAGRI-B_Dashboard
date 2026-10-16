import { useMemo } from 'react';
import EChartsGroupedBar from '../../charts/echarts/EChartsGroupedBar';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { getInitiativeShortName } from '../../../data/glossary';
import { useT } from '../../../i18n/LanguageContext';

/**
 * Overall accuracy bars + average line — ECharts edition (Fase 2 fatia 2c).
 * Replaces the Plotly `BaseChart` bar/avg-line (min–max range stays in the
 * summary cards); sorting, i18n and chrome unchanged.
 * Reversible: previous version in git history.
 */
export default function GlobalAccuracyTab() {
  const { t, locale } = useT('charts');
  const { t: tBody } = useT('initiative');
  const initiatives = useDashboardStore((s) => s.initiatives);

  const chartData = useMemo(() => {
    return initiatives
      .filter((i) => i.Accuracy > 0)
      .map((i) => ({
        name: getInitiativeShortName(i.Display_Name, locale),
        accuracy: i.Accuracy,
        accuracyMin: i.Accuracy_Min,
        accuracyMax: i.Accuracy_Max,
      }))
      .sort((a, b) => b.accuracy - a.accuracy);
  }, [initiatives, locale]);

  if (chartData.length === 0) {
    return <div className="py-8 text-center text-fg-muted">{tBody('noAccuracyData')}</div>;
  }

  const avgAccuracy =
    chartData.reduce((s, d) => s + d.accuracy, 0) / chartData.length;

  return (
    <div className="space-y-4">
      <p className="text-sm text-fg-secondary">
        {tBody('accuracyIntro')}
      </p>
      <p className="text-xs text-fg-muted" role="note">
        {tBody('overallScoreNote')}
      </p>
      <EChartsGroupedBar
        categories={chartData.map((d) => d.name)}
        series={[{ name: t('overallAccuracyPct'), values: chartData.map((d) => d.accuracy) }]}
        captionKey="overallAccuracyByInitiative"
        height={450}
        referenceLine={{
          value: avgAccuracy,
          name: `${t('average')} (${avgAccuracy.toFixed(1)}%)`,
        }}
      />

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="bg-surface rounded-lg border border-border p-3 text-center">
          <div className="text-xs text-fg-secondary">{tBody('cardAvgAccuracy')}</div>
          <div className="text-lg font-bold text-emerald-600">{avgAccuracy.toFixed(1)}%</div>
        </div>
        <div className="bg-surface rounded-lg border border-border p-3 text-center">
          <div className="text-xs text-fg-secondary">{tBody('cardHighestAccuracy')}</div>
          <div className="text-lg font-bold text-blue-600">
            {Math.max(...chartData.map((d) => d.accuracy)).toFixed(1)}%
          </div>
        </div>
        <div className="bg-surface rounded-lg border border-border p-3 text-center">
          <div className="text-xs text-fg-secondary">{tBody('cardLowestAccuracy')}</div>
          <div className="text-lg font-bold text-orange-600">
            {Math.min(...chartData.map((d) => d.accuracy)).toFixed(1)}%
          </div>
        </div>
      </div>
    </div>
  );
}
