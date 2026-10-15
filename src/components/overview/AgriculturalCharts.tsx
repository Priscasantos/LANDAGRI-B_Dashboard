import { useMemo } from 'react';
import ChartContainer from '../charts/ChartContainer';
import { RechartsLineChart } from '../charts/recharts/RechartsLineChart';
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

  if (lineSeries.length === 0) return null;

  return (
    <section className="space-y-6 mt-8" aria-labelledby="agri-charts-heading">
      <h2 id="agri-charts-heading" className="text-xl font-bold text-fg">
        🌾 Brazilian Agricultural Data
      </h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartContainer
          title="Agricultural Production Evolution (thousands of tons)"
          description="IBGE PAM/PPM e CONAB"
        >
          <RechartsLineChart
            title="Agricultural Production Evolution (thousands of tons)"
            series={lineSeries}
            xlabel="Year"
            ylabel="Production (x1000 tons)"
          />
        </ChartContainer>
        <ChartContainer
          title={`Production Distribution${latestYear ? ` (${latestYear})` : ' (Latest Year)'}`}
          description="IBGE PAM/PPM e CONAB"
        >
          <RechartsPieChart
            title={`Production Distribution${latestYear ? ` (${latestYear})` : ' (Latest Year)'}`}
            data={pieSlices}
          />
        </ChartContainer>
      </div>
      <ChartContainer
        title="Average Area Harvested (thousands of hectares)"
        description="IBGE PAM/PPM e CONAB"
      >
        <RechartsBarChart
          title="Average Area Harvested (thousands of hectares)"
          data={barData}
          xlabel="Product"
          ylabel="Area (x1000 ha)"
        />
      </ChartContainer>
      <p className="text-xs text-fg-muted">
        Fonte: IBGE PAM/PPM e CONAB — dados processados em `src/data/processed/`.
      </p>
    </section>
  );
}
