import { useMemo } from 'react';
import BaseChart from '../../charts/BaseChart';
import type { Data } from 'plotly.js';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { CATEGORICAL_COLORS } from '../../../types/theme';
import { useT } from '../../../i18n/LanguageContext';

export default function ClassDetailsTab() {
  const { t } = useT('charts');
  const { t: tBody } = useT('initiative');
  const initiatives = useDashboardStore((s) => s.initiatives);

  const chartData = useMemo(() => {
    return initiatives
      .filter((i) => i.Number_of_Classes > 0)
      .map((i) => ({
        name: i.Display_Name,
        totalClasses: i.Number_of_Classes,
        agriClasses: i.Number_of_Agriculture_Classes,
        agriFocus:
          i.Number_of_Classes > 0
            ? Math.round((i.Number_of_Agriculture_Classes / i.Number_of_Classes) * 100)
            : 0,
        capabilities: i.Agricultural_Capabilities || 'N/A',
      }))
      .sort((a, b) => b.totalClasses - a.totalClasses);
  }, [initiatives]);

  if (chartData.length === 0) {
    return <div className="py-8 text-center text-fg-muted">{tBody('noClassData')}</div>;
  }

  // Total classes bar
  const classesBar: Data = {
    x: chartData.map((d) => d.name),
    y: chartData.map((d) => d.totalClasses),
    type: 'bar',
    name: t('totalClasses'),
    marker: { color: chartData.map((_, i) => CATEGORICAL_COLORS[i % CATEGORICAL_COLORS.length]) },
    text: chartData.map((d) => String(d.totalClasses)),
    textposition: 'outside',
    hovertemplate: `<b>%{x}</b><br>${t('totalClasses')}: %{y}<extra></extra>`,
  };

  // Agriculture focus pie
  const totalAgri = chartData.reduce((s, d) => s + d.agriClasses, 0);
  const totalNonAgri = chartData.reduce((s, d) => s + d.totalClasses, 0) - totalAgri;
  const focusPie: Data = {
    labels: [t('agricultureClasses'), t('otherClasses')],
    values: [totalAgri, totalNonAgri],
    type: 'pie',
    marker: { colors: ['#22c55e', '#94a3b8'] },
    textinfo: 'label+percent',
    hovertemplate: `<b>%{label}</b><br>${t('count')}: %{value}<extra></extra>`,
  };

  // Capabilities visualization (horizontal bar of distinct capabilities)
  const capCount: Record<string, number> = {};
  chartData.forEach((d) => {
    const cap = d.capabilities || 'Unknown';
    capCount[cap] = (capCount[cap] || 0) + 1;
  });
  const capEntries = Object.entries(capCount)
    .map(([cap, count]) => ({ cap, count }))
    .sort((a, b) => b.count - a.count);

  const capBar: Data = {
    y: capEntries.map((d) => d.cap),
    x: capEntries.map((d) => d.count),
    type: 'bar',
    orientation: 'h',
    marker: { color: CATEGORICAL_COLORS.slice(0, capEntries.length) },
    text: capEntries.map((d) => String(d.count)),
    textposition: 'outside',
    hovertemplate: `<b>%{y}</b><br>${t('initiatives')}: %{x}<extra></extra>`,
  };

  // Grouped bar: total vs agri
  const groupedTraces: Data[] = [
    {
      name: t('totalClasses'),
      x: chartData.map((d) => d.name),
      y: chartData.map((d) => d.totalClasses),
      type: 'bar',
      marker: { color: '#3b82f6' },
      hovertemplate: `<b>%{x}</b><br>${t('total')}: %{y}<extra></extra>`,
    },
    {
      name: t('agricultureClasses'),
      x: chartData.map((d) => d.name),
      y: chartData.map((d) => d.agriClasses),
      type: 'bar',
      marker: { color: '#22c55e' },
      hovertemplate: `<b>%{x}</b><br>${t('agriculture')}: %{y}<extra></extra>`,
    },
  ];

  // Stacked bar: agri focus %
  const stackedTraces: Data[] = [
    {
      name: t('agriculture'),
      x: chartData.map((d) => d.name),
      y: chartData.map((d) => d.agriFocus),
      type: 'bar',
      marker: { color: '#22c55e' },
      hovertemplate: `<b>%{x}</b><br>${t('agricultureFocus')}: %{y}%<extra></extra>`,
    },
    {
      name: t('other'),
      x: chartData.map((d) => d.name),
      y: chartData.map((d) => 100 - d.agriFocus),
      type: 'bar',
      marker: { color: '#e2e8f0' },
      hovertemplate: `<b>%{x}</b><br>${t('other')}: %{y}%<extra></extra>`,
    },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-base font-semibold text-fg mb-2">{tBody('hTotalClasses')}</h3>
        <BaseChart
          data={[classesBar]}
          layout={{
            title: { text: t('numberOfClassesByInitiative'), x: 0 },
            xaxis: { title: '' },
            yaxis: { title: t('classes'), dtick: 1 },
            height: 400,
            margin: { l: 50, r: 20, t: 40, b: 120 },
          }}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-base font-semibold text-fg mb-2">{tBody('hAgriVsOther')}</h3>
          <BaseChart
            data={[focusPie]}
            layout={{
              title: { text: t('agricultureFocus'), x: 0 },
              height: 300,
            }}
          />
        </div>
        <div>
          <h3 className="text-base font-semibold text-fg mb-2">{tBody('hAgriCapabilities')}</h3>
          <BaseChart
            data={[capBar]}
            layout={{
              title: { text: t('capabilitiesDistribution'), x: 0 },
              xaxis: { title: t('initiatives'), dtick: 1 },
              yaxis: { title: '' },
              height: Math.max(250, capEntries.length * 40),
              margin: { l: 180, r: 40, t: 40, b: 50 },
            }}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-base font-semibold text-fg mb-2">{tBody('hTotalVsAgri')}</h3>
          <BaseChart
            data={groupedTraces}
            layout={{
              title: { text: t('classComparison'), x: 0 },
              xaxis: { title: '' },
              yaxis: { title: t('count') },
              barmode: 'group',
              height: 350,
              margin: { l: 50, r: 20, t: 40, b: 120 },
            }}
          />
        </div>
        <div>
          <h3 className="text-base font-semibold text-fg mb-2">{tBody('hAgriFocus')}</h3>
          <BaseChart
            data={stackedTraces}
            layout={{
              title: { text: t('agricultureFocusPercentage'), x: 0 },
              xaxis: { title: '' },
              yaxis: { title: t('percentagePct') },
              barmode: 'stack',
              height: 350,
              margin: { l: 50, r: 20, t: 40, b: 120 },
            }}
          />
        </div>
      </div>
    </div>
  );
}
