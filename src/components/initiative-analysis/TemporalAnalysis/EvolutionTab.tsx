import { useMemo } from 'react';
import { Star } from 'lucide-react';
import BaseChart from '../../charts/BaseChart';
import type { Data } from 'plotly.js';
import { useT } from '../../../i18n/LanguageContext';

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
  const { t } = useT('charts');
  const { t: tBody } = useT('initiative');
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
    name: t('activeInitiatives'),
    line: { color: '#14b8a6', width: 3 },
    marker: {
      color: activeByYear.map((d) => (d.year === peakYear ? '#f59e0b' : '#14b8a6')),
      size: activeByYear.map((d) => (d.year === peakYear ? 14 : 6)),
      symbol: activeByYear.map((d) => (d.year === peakYear ? 'star' : 'circle')),
      line: activeByYear.map((d) => (d.year === peakYear ? { width: 2, color: '#d97706' } : { width: 0 })) as unknown as Partial<{ color: string; width: number }>,
    },
    fill: 'tozeroy',
    fillcolor: 'rgba(20,184,166,0.15)',
    hovertemplate: `<b>%{x}</b><br>${t('activeInitiatives')}: %{y}<extra></extra>`,
  };

  // Average line as a scatter trace
  const avgTrace: Data = {
    x: [activeByYear[0]?.year ?? 0, activeByYear[activeByYear.length - 1]?.year ?? 0],
    y: [avgActive, avgActive],
    type: 'scatter',
    mode: 'lines',
    name: `${t('average')} (${avgActive})`,
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
    name: t('highRes'),
    stackgroup: 'resolution',
    line: { color: '#22c55e', width: 1 },
    fillcolor: 'rgba(34,197,94,0.6)',
    hovertemplate: `${t('highResShort')}: %{y}<extra></extra>`,
  };

  const resMedTrace: Data = {
    x: resolutionEvolution.years,
    y: resolutionEvolution.medium,
    type: 'scatter',
    mode: 'lines',
    name: t('mediumRes'),
    stackgroup: 'resolution',
    line: { color: '#eab308', width: 1 },
    fillcolor: 'rgba(234,179,8,0.6)',
    hovertemplate: `${t('mediumResShort')}: %{y}<extra></extra>`,
  };

  const resCoarseTrace: Data = {
    x: resolutionEvolution.years,
    y: resolutionEvolution.coarse,
    type: 'scatter',
    mode: 'lines',
    name: t('coarseRes'),
    stackgroup: 'resolution',
    line: { color: '#ef4444', width: 1 },
    fillcolor: 'rgba(239,68,68,0.6)',
    hovertemplate: `${t('coarseResShort')}: %{y}<extra></extra>`,
  };

  // Historical markers
  const markersTrace: Data = {
    x: [2000, 2020],
    y: [0, 0],
    type: 'scatter',
    mode: 'markers+text',
    name: t('historicalMilestones'),
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
        {tBody('noEvolutionData')}
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-base font-semibold text-fg mb-2">{tBody('activePerYear')}</h3>
        <p className="text-sm text-fg-secondary mb-3">
          {tBody('activePerYearIntroA')}{' '}
          <Star size={12} aria-hidden="true" className="inline-block align-[-1px]" /> {tBody('activePerYearIntroB')}
        </p>
        <BaseChart
          data={[activeTrace, avgTrace]}
          layout={{
            title: { text: t('activeInitiativesOverTime'), x: 0 },
            xaxis: { title: t('year') },
            yaxis: { title: t('activeInitiatives'), dtick: 1 },
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
                text: `${t('peak')}: ${peakYear}`,
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
        <h3 className="text-base font-semibold text-fg mb-2">{tBody('resolutionEvolution')}</h3>
        <p className="text-sm text-fg-secondary mb-3">
          {tBody('resolutionEvolutionIntro')}
        </p>
        <BaseChart
          data={[resCoarseTrace, resMedTrace, resHighTrace, markersTrace]}
          layout={{
            title: { text: t('resolutionDistributionOverTime'), x: 0 },
            xaxis: { title: t('year') },
            yaxis: { title: t('numberOfInitiatives') },
            hovermode: 'x unified',
            height: 400,
            barmode: 'stack',
          }}
        />
      </div>
    </div>
  );
}
