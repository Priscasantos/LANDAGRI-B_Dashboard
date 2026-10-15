import { useMemo } from 'react';
import { Wheat, BarChart3, MapPin, TrendingUp, CalendarDays, ClipboardList, RefreshCw } from 'lucide-react';
import Card from '../../ui/Card';
import Tabs from '../../ui/Tabs';
import DataTable from '../../ui/DataTable';
import MetricCard from '../../ui/MetricCard';
import HorizontalBarChart from '../../charts/HorizontalBarChart';
import LineChart from '../../charts/LineChart';
import ibgeData from '../../../data/processed/brazilian_ibge_agricultural_data.json';

interface IBGECropEntry {
  name: string;
  code: string;
  production_quantity_tonnes?: Record<string, number>;
  harvested_area_hectares?: Record<string, number>;
  planted_area_hectares?: Record<string, number>;
  average_yield?: Record<string, number>;
  production_value_thousand_reais?: Record<string, number>;
}

interface IBGEDataType {
  metadata?: {
    source?: string;
    survey?: string;
    period_range?: string;
    periodicity?: string;
  };
  data?: {
    agricultural_production?: Record<string, IBGECropEntry>;
  };
}

const REGIONS = ['North', 'Northeast', 'Southeast', 'South', 'Central-West'];

export default function IbgeEstimatesTab() {
  const data = ibgeData as IBGEDataType;
  const production = data?.data?.agricultural_production;

  const years = useMemo(() => {
    if (!production) return [];
    const yearSet = new Set<string>();
    for (const [, crop] of Object.entries(production)) {
      if (crop.production_quantity_tonnes) {
        Object.keys(crop.production_quantity_tonnes).forEach(y => yearSet.add(y));
      }
    }
    return Array.from(yearSet).sort();
  }, [production]);

  const topCrops = useMemo(() => {
    if (!production || years.length === 0) return [];
    const latestYear = years[years.length - 1];
    const items: { name: string; production: number; area: number }[] = [];

    for (const [, crop] of Object.entries(production)) {
      const prod = crop.production_quantity_tonnes?.[latestYear];
      const area = crop.harvested_area_hectares?.[latestYear];
      if (prod && prod > 0) {
        items.push({
          name: crop.name,
          production: prod,
          area: area || 0,
        });
      }
    }

    items.sort((a, b) => b.production - a.production);
    return items.slice(0, 10);
  }, [production, years]);

  const totalProductionEvolution = useMemo(() => {
    if (!production || years.length === 0) return { series: [] };
    const totals: Record<string, number> = {};
    for (const year of years) totals[year] = 0;

    for (const [, crop] of Object.entries(production)) {
      if (crop.production_quantity_tonnes) {
        for (const [year, val] of Object.entries(crop.production_quantity_tonnes)) {
          totals[year] = (totals[year] || 0) + val;
        }
      }
    }

    return {
      series: [{
        name: 'Total Production (tonnes)',
        x: years,
        y: years.map(y => totals[y] || 0),
        color: '#EC9706',
      }],
    };
  }, [production, years]);

  const areaEvolution = useMemo(() => {
    if (!production || years.length === 0) return { series: [] };
    const totals: Record<string, number> = {};
    for (const year of years) totals[year] = 0;

    for (const [, crop] of Object.entries(production)) {
      if (crop.harvested_area_hectares) {
        for (const [year, val] of Object.entries(crop.harvested_area_hectares)) {
          totals[year] = (totals[year] || 0) + val;
        }
      }
    }

    return {
      series: [{
        name: 'Harvested Area (hectares)',
        x: years,
        y: years.map(y => totals[y] || 0),
        color: '#626C01',
      }],
    };
  }, [production, years]);

  const top5Evolution = useMemo(() => {
    if (!production || years.length === 0) return { series: [] };
    const items: { name: string; production: number }[] = [];
    const latestYear = years[years.length - 1];

    for (const [, crop] of Object.entries(production)) {
      const prod = crop.production_quantity_tonnes?.[latestYear];
      if (prod) items.push({ name: crop.name, production: prod });
    }

    items.sort((a, b) => b.production - a.production);
    const top5 = items.slice(0, 5).map(i => i.name);

    const series = top5.map(name => {
      const entry = Object.values(production).find(c => c.name === name);
      if (!entry?.production_quantity_tonnes) return null;
      return {
        name,
        x: years,
        y: years.map(y => entry.production_quantity_tonnes![y] || 0),
      };
    }).filter(Boolean) as { name: string; x: string[]; y: number[] }[];

    return { series };
  }, [production, years]);

  const tableColumns = [
    { key: 'name', label: 'Crop' },
    { key: 'production', label: 'Production (tonnes)', format: (v: unknown) => (v as number)?.toLocaleString() || '-' },
    { key: 'area', label: 'Harvested Area (ha)', format: (v: unknown) => (v as number)?.toLocaleString() || '-' },
  ];

  if (!production || Object.keys(production).length === 0) {
    return (
      <div className="p-8 text-center text-fg-secondary">
        <p className="text-lg">No IBGE estimates data available.</p>
        <p className="text-sm mt-2">The IBGE data file may be empty or in an unexpected format.</p>
      </div>
    );
  }

  const productionByCropContent = (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card padding="lg" hover={false}>
          <h3 className="text-base font-semibold text-fg mb-3">Top 10 Crops by Production</h3>
          {topCrops.length > 0 ? (
            <HorizontalBarChart
              y={topCrops.map(c => c.name)}
              x={topCrops.map(c => c.production / 1000000)}
              xlabel="Production (million tonnes)"
              color="#EC9706"
              height={Math.max(300, topCrops.length * 35)}
            />
          ) : (
            <p className="text-fg-muted text-center py-8">No data available.</p>
          )}
        </Card>

        <Card padding="lg" hover={false}>
          <h3 className="text-base font-semibold text-fg mb-3">Crop Data Table</h3>
          <DataTable
            columns={tableColumns}
            data={topCrops as unknown as Record<string, unknown>[]}
          />
        </Card>
      </div>
    </div>
  );

  const regionalContent = (
    <div className="space-y-6">
      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-3">Regional Distribution Indicators</h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          {REGIONS.map(region => (
            <div key={region} className="bg-amber-50 rounded-lg p-3 text-center border border-amber-200">
              <p className="text-xs text-amber-700 font-medium">{region}</p>
              <p className="text-lg font-bold text-amber-900 mt-1"><Wheat size={20} aria-hidden="true" className="mx-auto" /></p>
              <p className="text-xs text-amber-600">Major producer</p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );

  const historicalContent = (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card padding="lg" hover={false}>
          <h3 className="text-base font-semibold text-fg mb-3">Total Production Evolution</h3>
          <LineChart series={totalProductionEvolution.series} xlabel="Year" ylabel="Production (tonnes)" height={350} />
        </Card>

        <Card padding="lg" hover={false}>
          <h3 className="text-base font-semibold text-fg mb-3">Harvested Area Evolution</h3>
          <LineChart series={areaEvolution.series} xlabel="Year" ylabel="Area (hectares)" height={350} />
        </Card>
      </div>

      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-3">Top 5 Crops — Production Evolution</h3>
        {top5Evolution.series.length > 0 ? (
          <LineChart series={top5Evolution.series} xlabel="Year" ylabel="Production (tonnes)" height={400} />
        ) : (
          <p className="text-fg-muted text-center py-8">No data available.</p>
        )}
      </Card>
    </div>
  );

  const subTabs = [
    { id: 'production', label: 'Production by Crop', icon: BarChart3, content: productionByCropContent },
    { id: 'regional', label: 'Regional Distribution', icon: MapPin, content: regionalContent },
    { id: 'historical', label: 'Historical Series', icon: TrendingUp, content: historicalContent },
  ];

  return (
    <div className="space-y-6">
      {/* Metric cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard icon={BarChart3} label="Crops Tracked" value={Object.keys(production).length} variant="accuracy" />
        <MetricCard icon={CalendarDays} label="Period" value={data?.metadata?.period_range || years.join('-')} variant="frequency" />
        <MetricCard icon={ClipboardList} label="Survey" value={data?.metadata?.survey?.split(' ')[0] || 'PAM'} variant="resolution" />
        <MetricCard icon={RefreshCw} label="Frequency" value={data?.metadata?.periodicity || 'Annual'} variant="classes" />
      </div>

      <Tabs tabs={subTabs} />
    </div>
  );
}
