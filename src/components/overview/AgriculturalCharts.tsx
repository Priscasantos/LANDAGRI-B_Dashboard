import { useMemo } from 'react';
import { Wheat } from 'lucide-react';
import ChartContainer from '../charts/ChartContainer';
import { RechartsLineChart } from '../charts/recharts/RechartsLineChart';
import { useT } from '../../i18n/LanguageContext';
import type { RechartsLineSeries } from '../charts/recharts/RechartsLineChart';
import { RechartsPieChart } from '../charts/recharts/RechartsPieChart';
import type { RechartsPieSlice } from '../charts/recharts/RechartsPieChart';
import { RechartsBarChart } from '../charts/recharts/RechartsBarChart';
import type { RechartsBarDatum } from '../charts/recharts/RechartsBarChart';
import brazilianAgriData from '../../data/processed/brazilian_agricultural_data.json';

interface ProductEntry {
  nome: string;
  codigo: string;
  quantidade_produzida_toneladas?: Record<string, number>;
  area_colhida_hectares?: Record<string, number>;
}

interface AgriChartsData {
  lineSeries: RechartsLineSeries[];
  pieSlices: RechartsPieSlice[];
  barData: RechartsBarDatum[];
  latestYear: number | null;
}

function buildAgriChartsData(): AgriChartsData {
  const empty: AgriChartsData = { lineSeries: [], pieSlices: [], barData: [], latestYear: null };
  try {
    const data = brazilianAgriData as Record<string, unknown>;
    const producao = (data as Record<string, Record<string, Record<string, ProductEntry>>>)?.data
      ?.producao_agricola;
    if (!producao) return empty;

    const productKeys = Object.keys(producao).slice(0, 8);
    const years = new Set<number>();
    const series: { name: string; values: Record<number, number> }[] = [];

    productKeys.forEach((productKey) => {
      const prod = producao[productKey];
      const productionByYear = prod.quantidade_produzida_toneladas ?? {};
      const values: Record<number, number> = {};
      Object.entries(productionByYear).forEach(([key, val]) => {
        const year = parseInt(key, 10);
        if (!isNaN(year) && typeof val === 'number') {
          years.add(year);
          values[year] = val;
        }
      });
      series.push({ name: prod.nome || productKey, values });
    });

    const sortedYears = Array.from(years).sort((a, b) => a - b);
    const lineSeries: RechartsLineSeries[] = series.map((s) => ({
      name: s.name,
      data: sortedYears.map((y) => ({ x: y, y: Math.round(((s.values[y] ?? 0) / 1000) * 10) / 10 })),
    }));

    const latestYear = sortedYears.length > 0 ? sortedYears[sortedYears.length - 1] : null;
    const pieSlices: RechartsPieSlice[] = latestYear
      ? series
          .map((s) => ({ label: s.name, value: s.values[latestYear] || 0 }))
          .sort((a, b) => b.value - a.value)
          .slice(0, 10)
      : [];

    const barData: RechartsBarDatum[] = productKeys
      .map((productKey) => {
        const prod = producao[productKey];
        const areaByYear = prod.area_colhida_hectares ?? {};
        const yearValues = Object.entries(areaByYear)
          .filter(([key]) => !isNaN(parseInt(key, 10)))
          .map(([, val]) => val);
        const avg =
          yearValues.length > 0
            ? yearValues.reduce((sum, v) => sum + v, 0) / yearValues.length
            : 0;
        return {
          category: prod.nome || productKey,
          value: Math.round((avg / 1000) * 10) / 10,
        };
      })
      .sort((a, b) => b.value - a.value)
      .slice(0, 10);

    return { lineSeries, pieSlices, barData, latestYear };
  } catch (err) {
    console.error('Error processing agricultural data:', err);
    return empty;
  }
}

/**
 * Brazilian agricultural charts (IBGE/CONAB/MapBiomas) — recharts edition (Fase 2).
 * Replaces the plotly `BaseChart` version so the Overview route no longer
 * pulls the ~3MB plotly bundle; remaining plotly charts load lazily via
 * `PlotlyLazyChart`. Reversible: previous version kept in git history.
 */
export default function AgriculturalCharts(): React.JSX.Element | null {
  const { lineSeries, pieSlices, barData, latestYear } = useMemo(() => buildAgriChartsData(), []);
  const { t } = useT('charts');
  const { t: tBody } = useT('agricultural');

  if (lineSeries.length === 0) return null;

  const distributionTitle =
    latestYear === null
      ? t('agriProductionDistributionLatest')
      : t('agriProductionDistribution', { year: latestYear });

  return (
    <section className="space-y-6 mt-8 min-w-0" aria-labelledby="agri-charts-heading">
      <h2 id="agri-charts-heading" className="flex items-center gap-1.5 text-xl font-bold text-fg">
        <Wheat size={20} aria-hidden="true" className="shrink-0" /> {tBody('hAgriData')}
      </h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 min-w-0">
        <ChartContainer
          title={t('agriProductionEvolution')}
          description={tBody('sourceAttribution')}
          className="min-w-0"
        >
          <RechartsLineChart
            title={t('agriProductionEvolution')}
            series={lineSeries}
            xlabel={t('year')}
            ylabel={t('productionKtons')}
          />
        </ChartContainer>
        <ChartContainer
          title={distributionTitle}
          description="IBGE PAM/PPM e CONAB"
          className="min-w-0"
        >
          <RechartsPieChart
            title={distributionTitle}
            data={pieSlices}
          />
        </ChartContainer>
      </div>
      <ChartContainer
        title={t('agriAvgArea')}
        description="IBGE PAM/PPM e CONAB"
        className="min-w-0"
      >
        <RechartsBarChart
          title={t('agriAvgArea')}
          data={barData}
          xlabel={t('product')}
          ylabel={t('areaKha')}
        />
      </ChartContainer>
      <p className="text-xs text-fg-muted">
        {tBody('sourceNote')}
      </p>
    </section>
  );
}
