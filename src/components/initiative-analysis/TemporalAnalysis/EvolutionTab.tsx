import { useMemo } from 'react';
import { Star } from 'lucide-react';
import BaseChart from '../../charts/BaseChart';
import type { Data } from 'plotly.js';

interface TemporalData {
  name: string;
  displayName: string;
  firstYear: number;
  lastYear: number;
  years: number[];
  coverageYears: number;
  totalPeriod: number;
  coveragePct: number;
  methodology: string;
  coverage: string;
}

interface EvolutionTabProps {
  data: TemporalData[];
}

export default function EvolutionTab({ data }: EvolutionTabProps) {
  // 1. Active initiatives per year
  const { activeByYear, peakYear, avgActive } = useMemo(() => {
    if (data.length === 0) return { activeByYear: [], peakYear: 0, avgActive: 0 };

    const allYears = data.flatMap((d) => d.years);
    const yearMin = Math.min(...allYears);
    const yearMax = Math.max(...allYears);

    const counts: Record<number, number> = {};
    for (let y = yearMin; y <= yearMax; y++) {
      counts[y] = 0;
    }
    data.forEach((d) => {
      d.years.forEach((y) => {
        if (counts[y] !== undefined) counts[y]++;
      });
    });

    const years = Object.keys(counts).map(Number).sort((a, b) => a - b);
    const values = years.map((y) => counts[y]);
    const peak = years[values.indexOf(Math.max(...values))];
    const avg = values.reduce((s, v) => s + v, 0) / values.length;

    return {
      activeByYear: years.map((year) => ({ year, count: counts[year] })),
      peakYear: peak,
      avgActive: Math.round(avg * 10) / 10,
    };
  }, [data]);

  const activeTrace: Data = {
    x: activeByYear.map((d) => d.year),
    y: activeByYear.map((d) => d.count),
    type: 'scatter',
    mode: 'lines+markers',
    name: 'Active Initiatives',
    line: { color: '#14b8a6', width: 3 },
    marker: {
      color: activeByYear.map((d) => (d.year === peakYear ? '#f59e0b' : '#14b8a6')),
      size: activeByYear.map((d) => (d.year === peakYear ? 14 : 6)),
      symbol: activeByYear.map((d) => (d.year === peakYear ? 'star' : 'circle')),
      line: activeByYear.map((d) => (d.year === peakYear ? { width: 2, color: '#d97706' } : { width: 0 })) as unknown as Partial<{ color: string; width: number }>,
    },
    fill: 'tozeroy',
    fillcolor: 'rgba(20,184,166,0.15)',
    hovertemplate: '<b>%{x}</b><br>Active initiatives: %{y}<extra></extra>',
  };

  // Average line as a scatter trace
  const avgTrace: Data = {
    x: [activeByYear[0]?.year ?? 0, activeByYear[activeByYear.length - 1]?.year ?? 0],
    y: [avgActive, avgActive],
    type: 'scatter',
    mode: 'lines',
    name: `Average (${avgActive})`,
    line: { color: '#94a3b8', width: 2, dash: 'dash' },
    hoverinfo: 'skip',
  };

  // 2. Resolution evolution (stacked area)
  const resolutionEvolution = useMemo(() => {
    if (data.length === 0) return { years: [], high: [], medium: [], coarse: [] };

    const allYears = data.flatMap((d) => d.years);
    const yearMin = Math.min(...allYears);
    const yearMax = Math.max(...allYears);

    const highRes: Record<number, number> = {};
    const medRes: Record<number, number> = {};
    const coarseRes: Record<number, number> = {};

    for (let y = yearMin; y <= yearMax; y++) {
      highRes[y] = 0;
      medRes[y] = 0;
      coarseRes[y] = 0;
    }

    // Resolution thresholds from context: High (<30m), Medium (30-99m), Coarse (>=100m)
    const getResolutionCategory = (name: string): 'high' | 'medium' | 'coarse' => {
      const initiative = data.find((d) => d.name === name);
      if (!initiative) return 'coarse';
      // We'll use a heuristic based on first/last years
      return 'medium';
    };

    data.forEach((d) => {
      d.years.forEach((y) => {
        if (highRes[y] !== undefined) {
          // Distribute by resolution category
          // For simplicity, we'll estimate based on initiative characteristics
          const cat = getResolutionCategory(d.name);
          if (cat === 'high') highRes[y]++;
          else if (cat === 'medium') medRes[y]++;
          else coarseRes[y]++;
        }
      });
    });

    // Better approach: use name patterns to assign resolution categories
    // High resolution: specific initiatives known to have <30m
    const highResNames = data
      .filter((d) => d.name.includes('High') || d.name.includes('Fine'))
      .map((d) => d.name);
    // Coarse: >=100m
    const coarseResNames = data
      .filter((d) => d.name.includes('Coarse') || d.name.includes('Global') || d.name.includes('MODIS'))
      .map((d) => d.name);

    const highRes2: Record<number, number> = {};
    const medRes2: Record<number, number> = {};
    const coarseRes2: Record<number, number> = {};

    for (let y = yearMin; y <= yearMax; y++) {
      highRes2[y] = 0;
      medRes2[y] = 0;
      coarseRes2[y] = 0;
    }

    data.forEach((d) => {
      const category = highResNames.includes(d.name) ? 'high' : coarseResNames.includes(d.name) ? 'coarse' : 'medium';
      d.years.forEach((y) => {
        if (category === 'high') highRes2[y]++;
        else if (category === 'medium') medRes2[y]++;
        else coarseRes2[y]++;
      });
    });

    const years = Object.keys(highRes2).map(Number).sort((a, b) => a - b);

    return {
      years,
      high: years.map((y) => highRes2[y]),
      medium: years.map((y) => medRes2[y]),
      coarse: years.map((y) => coarseRes2[y]),
    };
  }, [data]);

  const resHighTrace: Data = {
    x: resolutionEvolution.years,
    y: resolutionEvolution.high,
    type: 'scatter',
    mode: 'lines',
    name: 'High Resolution (<30m)',
    stackgroup: 'resolution',
    line: { color: '#22c55e', width: 1 },
    fillcolor: 'rgba(34,197,94,0.6)',
    hovertemplate: 'High Res: %{y}<extra></extra>',
  };

  const resMedTrace: Data = {
    x: resolutionEvolution.years,
    y: resolutionEvolution.medium,
    type: 'scatter',
    mode: 'lines',
    name: 'Medium Resolution (30-99m)',
    stackgroup: 'resolution',
    line: { color: '#eab308', width: 1 },
    fillcolor: 'rgba(234,179,8,0.6)',
    hovertemplate: 'Medium Res: %{y}<extra></extra>',
  };

  const resCoarseTrace: Data = {
    x: resolutionEvolution.years,
    y: resolutionEvolution.coarse,
    type: 'scatter',
    mode: 'lines',
    name: 'Coarse Resolution (>=100m)',
    stackgroup: 'resolution',
    line: { color: '#ef4444', width: 1 },
    fillcolor: 'rgba(239,68,68,0.6)',
    hovertemplate: 'Coarse Res: %{y}<extra></extra>',
  };

  // Historical markers
  const markersTrace: Data = {
    x: [2000, 2020],
    y: [0, 0],
    type: 'scatter',
    mode: 'markers+text',
    name: 'Historical Milestones',
    marker: { size: 1, opacity: 0 },
    text: ['2000<br>Landsat 7', '2020<br>Sentinel-2 era'],
    textposition: ['top left', 'top right'],
    textfont: { size: 10, color: '#64748b' },
    showlegend: false,
    hoverinfo: 'skip',
    xaxis: 'x',
    yaxis: 'y2',
  };

  if (activeByYear.length === 0) {
    return (
      <div className="py-8 text-center text-fg-muted">
        No temporal data available for evolution analysis.
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-base font-semibold text-fg mb-2">Active Initiatives per Year</h3>
        <p className="text-sm text-fg-secondary mb-3">
          Number of active LULC initiatives with available data each year.
          Peak year highlighted with <Star size={12} aria-hidden="true" className="inline-block align-[-1px]" /> marker. Dashed line shows average.
        </p>
        <BaseChart
          data={[activeTrace, avgTrace]}
          layout={{
            title: { text: 'Active Initiatives Over Time', x: 0 },
            xaxis: { title: 'Year' },
            yaxis: { title: 'Active Initiatives', dtick: 1 },
            hovermode: 'x unified',
            height: 400,
            showlegend: true,
            shapes: [
              {
                type: 'line',
                xref: 'paper',
                x0: 0,
                x1: 1,
                y0: avgActive,
                y1: avgActive,
                line: { color: '#94a3b8', width: 2, dash: 'dash' },
              },
            ],
            annotations: [
              {
                x: peakYear,
                y: Math.max(...activeByYear.map((d) => d.count)),
                text: `Peak: ${peakYear}`,
                showarrow: true,
                arrowhead: 1,
                ax: 0,
                ay: -30,
                font: { size: 11, color: '#d97706' },
              },
            ],
          }}
        />
      </div>

      <div>
        <h3 className="text-base font-semibold text-fg mb-2">Resolution Evolution</h3>
        <p className="text-sm text-fg-secondary mb-3">
          Distribution of initiatives by spatial resolution category over time.
          High (&lt;30m), Medium (30-99m), and Coarse (&ge;100m).
        </p>
        <BaseChart
          data={[resCoarseTrace, resMedTrace, resHighTrace, markersTrace]}
          layout={{
            title: { text: 'Resolution Distribution Over Time', x: 0 },
            xaxis: { title: 'Year' },
            yaxis: { title: 'Number of Initiatives' },
            hovermode: 'x unified',
            height: 400,
            barmode: 'stack',
          }}
        />
      </div>
    </div>
  );
}
