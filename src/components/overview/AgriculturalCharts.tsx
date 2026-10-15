import { useMemo } from 'react';
import { Wheat } from 'lucide-react';
import Card from '../ui/Card';
import EChartsLine from '../charts/echarts/EChartsLine';
import EChartsGroupedBar from '../charts/echarts/EChartsGroupedBar';
import EChartsBase from '../charts/echarts/EChartsBase';
import { buildPieOption } from '../charts/echarts/echarts-options';
import { useEffectiveTheme } from '../../hooks/use-theme';
import { useChartFontFamily } from '../../hooks/use-chart-font';
import { useT } from '../../i18n/LanguageContext';
import brazilianAgriData from '../../data/processed/brazilian_agricultural_data.json';

interface ProductEntry {
  nome: string;
  codigo: string;
  quantidade_produzida_toneladas?: Record<string, number>;
  area_colhida_hectares?: Record<string, number>;
}

interface LinePoint {
  x: number;
  y: number;
}

interface LineSeries {
  name: string;
  data: LinePoint[];
}

interface PieSlice {
  label: string;
  value: number;
}

interface BarDatum {
  category: string;
  value: number;
}

interface AgriChartsData {
  lineSeries: LineSeries[];
  pieSlices: PieSlice[];
  barData: BarDatum[];
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
    const lineSeries: LineSeries[] = series.map((s) => ({
      name: s.name,
      data: sortedYears.map((y) => ({ x: y, y: Math.round(((s.values[y] ?? 0) / 1000) * 10) / 10 })),
    }));

    const latestYear = sortedYears.length > 0 ? sortedYears[sortedYears.length - 1] : null;
    const pieSlices: PieSlice[] = latestYear
      ? series
          .map((s) => ({ label: s.name, value: s.values[latestYear] || 0 }))
          .sort((a, b) => b.value - a.value)
          .slice(0, 10)
      : [];

    const barData: BarDatum[] = productKeys
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
 * Brazilian agricultural charts (IBGE/CONAB/MapBiomas) — ECharts edition
 * (Fase 2 fatia 2c). Replaces the recharts wrappers so the Overview route
 * no longer pulls recharts wrappers; data shaping, i18n and chrome
 * unchanged. Reversible: previous version kept in git history.
 */
export default function AgriculturalCharts(): React.JSX.Element | null {
  const { lineSeries, pieSlices, barData, latestYear } = useMemo(() => buildAgriChartsData(), []);
  const { t, locale } = useT('charts');
  const { t: tBody } = useT('agricultural');
  const theme = useEffectiveTheme();
  const fontFamily = useChartFontFamily();

  const pieOption = useMemo(
    () =>
      buildPieOption({
        slices: pieSlices,
        theme,
        locale,
        fontFamily,
        donut: true,
      }),
    [pieSlices, theme, locale, fontFamily],
  );

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
        <Card padding="lg" hover={false} className="min-w-0">
          <h3 className="text-base font-semibold text-fg mb-1">{t('agriProductionEvolution')}</h3>
          <p className="text-xs text-fg-muted mb-3">{tBody('sourceAttribution')}</p>
          <EChartsLine
            series={lineSeries.map((s) => ({
              name: s.name,
              x: s.data.map((p) => p.x),
              y: s.data.map((p) => p.y),
            }))}
            captionKey="agriProductionEvolution"
            height={350}
          />
        </Card>
        <Card padding="lg" hover={false} className="min-w-0">
          <h3 className="text-base font-semibold text-fg mb-1">{distributionTitle}</h3>
          <p className="text-xs text-fg-muted mb-3">IBGE PAM/PPM e CONAB</p>
          <EChartsBase
            option={pieOption}
            ariaLabel={distributionTitle}
            caption={distributionTitle}
            height={350}
          />
        </Card>
      </div>
      <Card padding="lg" hover={false} className="min-w-0">
        <h3 className="text-base font-semibold text-fg mb-1">{t('agriAvgArea')}</h3>
        <p className="text-xs text-fg-muted mb-3">IBGE PAM/PPM e CONAB</p>
        <EChartsGroupedBar
          categories={barData.map((d) => d.category)}
          series={[{ name: t('areaKha'), values: barData.map((d) => d.value) }]}
          captionKey="agriAvgArea"
          height={350}
        />
      </Card>
      <p className="text-xs text-fg-muted">
        {tBody('sourceNote')}
      </p>
    </section>
  );
}
