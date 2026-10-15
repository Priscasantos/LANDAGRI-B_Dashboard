import { useMemo } from 'react';
import { Star } from 'lucide-react';
import EChartsLine from '../../charts/echarts/EChartsLine';
import type { EChartsLinePoint } from '../../charts/echarts/echarts-options';
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

/**
 * Active initiatives + resolution evolution — ECharts edition (Fase 2 fatia 2c).
 * Replaces the Plotly `BaseChart` line/area charts; computations, i18n and
 * chrome unchanged. Peak year keeps its marker via `markPoint`.
 * Reversible: previous version in git history.
 */
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

  const activeSeries: EChartsLinePoint[] = useMemo(() => {
    if (activeByYear.length === 0) return [];
    return [
      {
        name: t('activeInitiatives'),
        x: activeByYear.map((d) => d.year),
        y: activeByYear.map((d) => d.count),
        markPoint: { x: peakYear, label: `${t('peak')}: ${peakYear}` },
      },
      {
        name: `${t('average')} (${avgActive})`,
        x: [activeByYear[0]?.year ?? 0, activeByYear[activeByYear.length - 1]?.year ?? 0],
        y: [avgActive, avgActive],
        dash: 'dash',
      },
    ];
  }, [activeByYear, peakYear, avgActive, t]);

  // 2. Resolution evolution (stacked area)
  const resolutionEvolution = useMemo(() => {
    if (data.length === 0) return { years: [], high: [], medium: [], coarse: [] };

    const allYears = data.flatMap((d) => d.years);
    const yearMin = Math.min(...allYears);
    const yearMax = Math.max(...allYears);

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

  const resolutionSeries: EChartsLinePoint[] = useMemo(
    () => [
      {
        name: t('coarseRes'),
        x: resolutionEvolution.years,
        y: resolutionEvolution.coarse,
      },
      {
        name: t('mediumRes'),
        x: resolutionEvolution.years,
        y: resolutionEvolution.medium,
      },
      {
        name: t('highRes'),
        x: resolutionEvolution.years,
        y: resolutionEvolution.high,
      },
    ],
    [resolutionEvolution, t],
  );

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
        <EChartsLine
          series={activeSeries}
          captionKey="activeInitiativesOverTime"
          height={400}
          areaFill
        />
      </div>

      <div>
        <h3 className="text-base font-semibold text-fg mb-2">{tBody('resolutionEvolution')}</h3>
        <p className="text-sm text-fg-secondary mb-3">
          {tBody('resolutionEvolutionIntro')}
        </p>
        <EChartsLine
          series={resolutionSeries}
          captionKey="resolutionDistributionOverTime"
          height={400}
          showMarkers={false}
          stack
        />
      </div>
    </div>
  );
}
