import { useMemo } from 'react';
import BaseChart from '../../charts/BaseChart';
import type { Data } from 'plotly.js';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { CATEGORICAL_COLORS } from '../../../types/theme';
import { useT } from '../../../i18n/LanguageContext';

export default function MethodologyDeepDiveTab() {
  const { t } = useT('charts');
  const { t: tBody } = useT('initiative');
  const initiatives = useDashboardStore((s) => s.initiatives);

  const { methods, methodData, methodAccuracy } = useMemo(() => {
    const methodMap: Record<string, { count: number; totalAccuracy: number; initiatives: string[] }> = {};

    initiatives.forEach((i) => {
      if (!methodMap[i.Methodology]) {
        methodMap[i.Methodology] = { count: 0, totalAccuracy: 0, initiatives: [] };
      }
      methodMap[i.Methodology].count++;
      if (i.Accuracy > 0) methodMap[i.Methodology].totalAccuracy += i.Accuracy;
      methodMap[i.Methodology].initiatives.push(i.Display_Name);
    });

    const methods = Object.keys(methodMap).sort();
    const methodData = methods.map((m) => ({
      method: m,
      count: methodMap[m].count,
      initiatives: methodMap[m].initiatives,
    }));
    const methodAccuracy = methods.map((m) => ({
      method: m,
      avgAccuracy:
        methodMap[m].count > 0
          ? Math.round((methodMap[m].totalAccuracy / methodMap[m].count) * 10) / 10
          : 0,
    }));

    return { methods, methodData, methodAccuracy };
  }, [initiatives]);

  if (methods.length === 0) {
    return <div className="py-8 text-center text-fg-muted">{tBody('noMethodologyData')}</div>;
  }

  // Pie: methodology distribution
  const pieTrace: Data = {
    labels: methodData.map((d) => d.method),
    values: methodData.map((d) => d.count),
    type: 'pie',
    marker: { colors: CATEGORICAL_COLORS.slice(0, methodData.length) },
    textinfo: 'label+percent',
    hovertemplate: `<b>%{label}</b><br>${t('count')}: %{value}<extra></extra>`,
  };

  // Horizontal bar: accuracy by methodology
  const hbarTrace: Data = {
    y: methodAccuracy.map((d) => d.method),
    x: methodAccuracy.map((d) => d.avgAccuracy),
    type: 'bar',
    orientation: 'h',
    marker: {
      color: methodAccuracy.map((_, i) => CATEGORICAL_COLORS[i % CATEGORICAL_COLORS.length]),
    },
    text: methodAccuracy.map((d) => `${d.avgAccuracy}%`),
    textposition: 'outside',
    hovertemplate: `<b>%{y}</b><br>${t('avgAccuracy')}: %{x}%<extra></extra>`,
  };

  // Line trend: accuracy trends by methodology over time (simplified - show method vs avg accuracy)
  const lineTraces: Data[] = methodAccuracy.map((d, i) => ({
    name: d.method,
    x: [d.method],
    y: [d.avgAccuracy],
    type: 'scatter',
    mode: 'markers',
    marker: {
      size: 16,
      color: CATEGORICAL_COLORS[i % CATEGORICAL_COLORS.length],
      line: { width: 2, color: 'white' },
    },
    hovertemplate: `<b>%{x}</b><br>${t('avgAccuracy')}: %{y:.1f}%<extra></extra>`,
  }));

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-base font-semibold text-fg mb-2">{tBody('hMethodologyDist')}</h3>
          <BaseChart
            data={[pieTrace]}
            layout={{
              title: { text: t('methodologyBreakdown'), x: 0 },
              height: 350,
            }}
          />
        </div>
        <div>
          <h3 className="text-base font-semibold text-fg mb-2">{tBody('hAvgByMethod')}</h3>
          <BaseChart
            data={[hbarTrace]}
            layout={{
              title: { text: t('accuracyByMethodology'), x: 0 },
              xaxis: { title: t('avgAccuracyPct') },
              yaxis: { title: '' },
              height: Math.max(250, methods.length * 50),
              margin: { l: 150, r: 40, t: 40, b: 50 },
            }}
          />
        </div>
      </div>

      {/* Accuracy comparison */}
      <div>
        <h3 className="text-base font-semibold text-fg mb-2">{tBody('hAccuracyTrends')}</h3>
        <p className="text-sm text-fg-secondary mb-3">
          {tBody('trendsIntro')}
        </p>
        <BaseChart
          data={lineTraces}
          layout={{
            title: { text: t('methodologyAccuracyComparison'), x: 0 },
            xaxis: { title: t('methodology') },
            yaxis: { title: t('avgAccuracyPct'), range: [0, 105] },
            height: 400,
            showlegend: true,
          }}
        />
      </div>

      {/* Summary table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="px-4 py-2 text-left font-semibold text-fg-secondary bg-surface-alt">{tBody('thMethodology')}</th>
              <th className="px-4 py-2 text-right font-semibold text-fg-secondary bg-surface-alt">{tBody('thCount')}</th>
              <th className="px-4 py-2 text-right font-semibold text-fg-secondary bg-surface-alt">{tBody('thAvgAccuracy')}</th>
            </tr>
          </thead>
          <tbody>
            {methodData.map((d, idx) => {
              const acc = methodAccuracy.find((a) => a.method === d.method);
              return (
                <tr key={d.method} className={`border-b border-border ${idx % 2 === 0 ? 'bg-surface' : 'bg-surface-alt'}`}>
                  <td className="px-4 py-2 text-fg">{d.method}</td>
                  <td className="px-4 py-2 text-right text-fg">{d.count}</td>
                  <td className="px-4 py-2 text-right text-fg">{acc?.avgAccuracy ?? '-'}%</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
