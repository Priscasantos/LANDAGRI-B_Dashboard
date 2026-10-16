import { useMemo } from 'react';
import EChartsGroupedBar from '../../charts/echarts/EChartsGroupedBar';
import EChartsHorizontalBar from '../../charts/echarts/EChartsHorizontalBar';
import EChartsPie from '../../charts/echarts/EChartsPie';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { getInitiativeShortName } from '../../../data/glossary';
import { useT } from '../../../i18n/LanguageContext';

/**
 * Class counts / agri focus / capabilities — ECharts edition (Fase 2 fatia 2c).
 * Replaces the five Plotly `BaseChart` charts (bar, pie, horizontal bar,
 * grouped + stacked bars); computations, i18n and chrome unchanged.
 * Reversible: previous version in git history.
 */
export default function ClassDetailsTab() {
  const { t, locale } = useT('charts');
  const { t: tBody } = useT('initiative');
  const initiatives = useDashboardStore((s) => s.initiatives);

  const chartData = useMemo(() => {
    return initiatives
      .filter((i) => i.Number_of_Classes > 0)
      .map((i) => ({
        name: getInitiativeShortName(i.Display_Name, locale),
        totalClasses: i.Number_of_Classes,
        agriClasses: i.Number_of_Agriculture_Classes,
        agriFocus:
          i.Number_of_Classes > 0
            ? Math.round((i.Number_of_Agriculture_Classes / i.Number_of_Classes) * 100)
            : 0,
        capabilities: i.Agricultural_Capabilities || 'N/A',
      }))
      .sort((a, b) => b.totalClasses - a.totalClasses);
  }, [initiatives, locale]);

  const { totalAgri, totalNonAgri, capEntries } = useMemo(() => {
    const totalAgri = chartData.reduce((s, d) => s + d.agriClasses, 0);
    const totalNonAgri = chartData.reduce((s, d) => s + d.totalClasses, 0) - totalAgri;
    const capCount: Record<string, number> = {};
    chartData.forEach((d) => {
      const cap = d.capabilities || 'Unknown';
      capCount[cap] = (capCount[cap] || 0) + 1;
    });
    const capEntries = Object.entries(capCount)
      .map(([cap, count]) => ({ cap, count }))
      .sort((a, b) => b.count - a.count);
    return { totalAgri, totalNonAgri, capEntries };
  }, [chartData]);

  if (chartData.length === 0) {
    return <div className="py-8 text-center text-fg-muted">{tBody('noClassData')}</div>;
  }

  const names = chartData.map((d) => d.name);

  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-base font-semibold text-fg mb-2">{tBody('hTotalClasses')}</h3>
        <EChartsGroupedBar
          categories={names}
          series={[{ name: t('totalClasses'), values: chartData.map((d) => d.totalClasses) }]}
          captionKey="numberOfClassesByInitiative"
          height={400}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-base font-semibold text-fg mb-2">{tBody('hAgriVsOther')}</h3>
          <EChartsPie
            data={[
              { label: t('agricultureClasses'), value: totalAgri },
              { label: t('otherClasses'), value: totalNonAgri },
            ]}
            captionKey="agricultureFocus"
            height={300}
          />
        </div>
        <div>
          <h3 className="text-base font-semibold text-fg mb-2">{tBody('hAgriCapabilities')}</h3>
          <EChartsHorizontalBar
            labels={capEntries.map((d) => d.cap)}
            values={capEntries.map((d) => d.count)}
            captionKey="capabilitiesDistribution"
            height={Math.max(250, capEntries.length * 40)}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-base font-semibold text-fg mb-2">{tBody('hTotalVsAgri')}</h3>
          <EChartsGroupedBar
            categories={names}
            series={[
              {
                name: t('totalClasses'),
                values: chartData.map((d) => d.totalClasses),
              },
              {
                name: t('agricultureClasses'),
                values: chartData.map((d) => d.agriClasses),
              },
            ]}
            captionKey="classComparison"
            height={350}
          />
        </div>
        <div>
          <h3 className="text-base font-semibold text-fg mb-2">{tBody('hAgriFocus')}</h3>
          <EChartsGroupedBar
            categories={names}
            series={[
              {
                name: t('agriculture'),
                values: chartData.map((d) => d.agriFocus),
              },
              {
                name: t('other'),
                values: chartData.map((d) => 100 - d.agriFocus),
              },
            ]}
            captionKey="agricultureFocusPercentage"
            height={350}
            stacked
          />
        </div>
      </div>
    </div>
  );
}
