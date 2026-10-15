import { useMemo } from 'react';
import EChartsPie from '../../charts/echarts/EChartsPie';
import EChartsHorizontalBar from '../../charts/echarts/EChartsHorizontalBar';
import EChartsLine from '../../charts/echarts/EChartsLine';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { translateMethodology } from '../../../data/glossary';
import { useT } from '../../../i18n/LanguageContext';

/**
 * Methodology deep-dive — ECharts edition (Fase 2 fatia 2c).
 * Replaces the three Plotly `BaseChart` charts (pie, horizontal accuracy
 * bar, per-methodology accuracy markers); aggregates, summary table, i18n
 * and chrome unchanged. Reversible: previous version in git history.
 */
export default function MethodologyDeepDiveTab() {
  const { t: tBody, locale } = useT('initiative');
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

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-base font-semibold text-fg mb-2">{tBody('hMethodologyDist')}</h3>
          <EChartsPie
            data={methodData.map((d) => ({ label: translateMethodology(d.method, locale), value: d.count }))}
            captionKey="methodologyBreakdown"
            height={350}
            donut
          />
        </div>
        <div>
          <h3 className="text-base font-semibold text-fg mb-2">{tBody('hAvgByMethod')}</h3>
          <EChartsHorizontalBar
            labels={methodAccuracy.map((d) => translateMethodology(d.method, locale))}
            values={methodAccuracy.map((d) => d.avgAccuracy)}
            captionKey="accuracyByMethodology"
            height={Math.max(250, methods.length * 50)}
          />
        </div>
      </div>

      {/* Accuracy comparison */}
      <div>
        <h3 className="text-base font-semibold text-fg mb-2">{tBody('hAccuracyTrends')}</h3>
        <p className="text-sm text-fg-secondary mb-3">
          {tBody('trendsIntro')}
        </p>
        <EChartsLine
          series={methodAccuracy.map((d) => ({
            name: translateMethodology(d.method, locale),
            x: [d.method],
            y: [d.avgAccuracy],
          }))}
          captionKey="methodologyAccuracyComparison"
          height={400}
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
                  <td className="px-4 py-2 text-fg">{translateMethodology(d.method, locale)}</td>
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
