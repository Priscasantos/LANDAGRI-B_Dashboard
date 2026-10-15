import { useMemo } from 'react';
import { Package, Sprout, TrendingUp, Wheat } from 'lucide-react';
import Card from '../../ui/Card';
import MetricCard from '../../ui/MetricCard';
import LineChart from '../../charts/LineChart';
import GroupedBarChart from '../../charts/GroupedBarChart';
import HorizontalBarChart from '../../charts/HorizontalBarChart';
import PieChart from '../../charts/PieChart';
import conabAgriculturalData from '../../../data/processed/conab_agricultural_data.json';

interface ProductionYear {
  production: number;
  area: number;
  productivity: number;
}

interface CropData {
  name: string;
  scientific_name?: string;
  production_data?: Record<string, ProductionYear>;
}

interface ConabAgriData {
  metadata?: {
    source?: string;
    description?: string;
    source_url?: string;
    unit_production?: string;
    unit_area?: string;
    total_crops?: number;
  };
  crops?: Record<string, CropData>;
}

export default function ConabEstimatesTab() {
  const data = conabAgriculturalData as ConabAgriData;
  const crops = data?.crops;

  const metrics = useMemo(() => {
    if (!crops) return { totalProduction: 0, totalArea: 0, avgProductivity: 0, cropCount: 0 };

    let totalProd = 0;
    let totalArea = 0;
    let totalProdWeighted = 0;
    let cropCount = 0;
    const seasons = ['2023/24', '2022/23', '2021/22', '2020/21', '2019/20', '2018/19'];
    const latestSeason = seasons[0];

    for (const [, crop] of Object.entries(crops)) {
      const pd = crop.production_data;
      if (pd && pd[latestSeason]) {
        totalProd += pd[latestSeason].production;
        totalArea += pd[latestSeason].area;
        totalProdWeighted += pd[latestSeason].production * pd[latestSeason].productivity;
        cropCount++;
      }
    }

    const avgProd = totalProd > 0 ? totalProdWeighted / totalProd : 0;

    return {
      totalProduction: totalProd,
      totalArea,
      avgProductivity: Math.round(avgProd),
      cropCount,
    };
  }, [crops]);

  const productionEvolution = useMemo(() => {
    if (!crops) return { series: [] };
    const seasons = ['2018/19', '2019/20', '2020/21', '2021/22', '2022/23', '2023/24'];

    const totalBySeason: Record<string, number> = {};
    for (const season of seasons) {
      totalBySeason[season] = 0;
      for (const [, crop] of Object.entries(crops)) {
        const pd = crop.production_data;
        if (pd && pd[season]) {
          totalBySeason[season] += pd[season].production;
        }
      }
    }

    return {
      series: [{
        name: 'Total Production (thousand tons)',
        x: seasons,
        y: seasons.map(s => totalBySeason[s]),
        color: '#EC9706',
      }],
    };
  }, [crops]);

  const cropComparison = useMemo(() => {
    if (!crops) return { categories: [], series: [] };
    const seasons = ['2018/19', '2019/20', '2020/21', '2021/22', '2022/23', '2023/24'];

    const productionSeries = Object.entries(crops).map(([, crop]) => ({
      name: crop.name,
      values: seasons.map((s) => {
        const pd = crop.production_data;
        return pd && pd[s] ? pd[s].production : 0;
      }),
    }));

    return { categories: seasons, series: productionSeries };
  }, [crops]);

  const soybeanCornProductivity = useMemo(() => {
    if (!crops) return { series: [] };
    const seasons = ['2018/19', '2019/20', '2020/21', '2021/22', '2022/23', '2023/24'];

    const series: { name: string; x: string[]; y: number[]; color?: string }[] = [];

    const addCrop = (key: string, name: string, color: string) => {
      const crop = crops[key];
      if (crop?.production_data) {
        series.push({
          name,
          x: seasons,
          y: seasons.map(s => crop.production_data![s]?.productivity || 0),
          color,
        });
      }
    };

    addCrop('soybean', 'Soybean', '#EC9706');
    addCrop('corn_total', 'Corn (Total)', '#626C01');

    return { series };
  }, [crops]);

  const plantedAreaDistribution = useMemo(() => {
    if (!crops) return [];
    const latestSeason = '2023/24';
    const slices: { label: string; value: number }[] = [];

    for (const [, crop] of Object.entries(crops)) {
      const pd = crop.production_data;
      if (pd && pd[latestSeason] && pd[latestSeason].area > 0) {
        slices.push({ label: crop.name, value: pd[latestSeason].area });
      }
    }

    slices.sort((a, b) => b.value - a.value);
    return slices;
  }, [crops]);

  const allCropsProduction = useMemo(() => {
    if (!crops) return { labels: [], values: [] };
    const latestSeason = '2023/24';
    const items: { label: string; value: number }[] = [];

    for (const [, crop] of Object.entries(crops)) {
      const pd = crop.production_data;
      if (pd && pd[latestSeason] && pd[latestSeason].production > 0) {
        items.push({ label: crop.name, value: pd[latestSeason].production });
      }
    }

    items.sort((a, b) => a.value - b.value);
    return {
      labels: items.map(i => i.label),
      values: items.map(i => i.value),
    };
  }, [crops]);

  if (!crops || Object.keys(crops).length === 0) {
    return (
      <div className="p-8 text-center text-fg-secondary">
        <p className="text-lg">No CONAB estimates data available.</p>
        <p className="text-sm mt-2">The agricultural data file may be empty or in an unexpected format.</p>
      </div>
    );
  }

  const unitProd = data?.metadata?.unit_production || 'thousand tons';
  const unitArea = data?.metadata?.unit_area || 'thousand hectares';

  return (
    <div className="space-y-6">
      {/* Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard icon={Package} label="Total Production" value={`${metrics.totalProduction.toLocaleString()}k ${unitProd.split(' ')[0]}`} variant="accuracy" />
        <MetricCard icon={Sprout} label="Planted Area" value={`${metrics.totalArea.toLocaleString()}k ha`} variant="resolution" />
        <MetricCard icon={TrendingUp} label="Avg Productivity" value={`${metrics.avgProductivity} kg/ha`} variant="classes" />
        <MetricCard icon={Wheat} label="Crops Tracked" value={metrics.cropCount} variant="frequency" />
      </div>

      {/* Production Evolution */}
      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-3">Production Evolution (Total Grains)</h3>
        <LineChart series={productionEvolution.series} xlabel="Season" ylabel={`Production (${unitProd})`} height={350} />
      </Card>

      {/* Crop Comparison */}
      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-3">Crop Comparison — Production by Season</h3>
        <GroupedBarChart
          categories={cropComparison.categories}
          series={cropComparison.series}
          xlabel="Season"
          ylabel={`Production (${unitProd})`}
          height={400}
        />
      </Card>

      {/* Soybean & Corn Productivity */}
      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-3">Productivity — Soybean &amp; Corn</h3>
        <LineChart series={soybeanCornProductivity.series} xlabel="Season" ylabel="Productivity (kg/ha)" height={350} />
      </Card>

      {/* Planted Area Distribution + All Crops by Production */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card padding="lg" hover={false}>
          <h3 className="text-base font-semibold text-fg mb-3">Planted Area Distribution ({unitArea})</h3>
          {plantedAreaDistribution.length > 0 ? (
            <PieChart data={plantedAreaDistribution} height={350} donut />
          ) : (
            <p className="text-fg-muted text-center py-8">No area data available.</p>
          )}
        </Card>

        <Card padding="lg" hover={false}>
          <h3 className="text-base font-semibold text-fg mb-3">All Crops by Production</h3>
          {allCropsProduction.values.length > 0 ? (
            <HorizontalBarChart
              y={allCropsProduction.labels}
              x={allCropsProduction.values}
              xlabel={`Production (${unitProd})`}
              color="#EC9706"
              height={Math.max(250, allCropsProduction.labels.length * 40)}
            />
          ) : (
            <p className="text-fg-muted text-center py-8">No production data available.</p>
          )}
        </Card>
      </div>

      {/* Source Info */}
      <Card padding="md" hover={false}>
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-semibold text-fg">Data Source</h4>
            <p className="text-xs text-fg-secondary">
              {data?.metadata?.source || 'CONAB'} &mdash; {data?.metadata?.description || 'Agricultural Production Data'}
            </p>
          </div>
          <a
            href={data?.metadata?.source_url || 'https://www.gov.br/conab/pt-br'}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-amber-700 hover:text-amber-800 underline"
          >
            Visit Source
          </a>
        </div>
      </Card>
    </div>
  );
}
