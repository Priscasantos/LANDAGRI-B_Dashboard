import { useMemo } from 'react';
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

interface CoverageTabProps {
  data: TemporalData[];
}

export default function CoverageTab({ data }: CoverageTabProps) {
  // locale reativo: ordenação e chrome do gráfico acompanham o toggle PT↔EN.
  const { t, locale } = useT('charts');
  const { t: tBody } = useT('initiative');
  const { matrix, yearLabels, sortedData, stats } = useMemo(() => {
    if (data.length === 0) return { matrix: [], yearLabels: [], sortedData: [], stats: null };

    const allYears = data.flatMap((d) => d.years);
    const yearMin = Math.min(...allYears);
    const yearMax = Math.max(...allYears);
    const years: number[] = [];
    for (let y = yearMin; y <= yearMax; y++) years.push(y);

    const sorted = [...data].sort((a, b) => a.firstYear - b.firstYear || a.displayName.localeCompare(b.displayName, locale));

    const mat = sorted.map((d) => years.map((y) => (d.years.includes(y) ? 1 : 0)));

    // Statistics
    const totalYears = years.length;
    const yearCoverage = years.map((y) => ({
      year: y,
      count: sorted.filter((d) => d.years.includes(y)).length,
    }));
    const bestYear = [...yearCoverage].sort((a, b) => b.count - a.count)[0];
    const worstYear = [...yearCoverage].sort((a, b) => a.count - b.count)[0];
    const avgCoverage = yearCoverage.reduce((s, d) => s + d.count, 0) / yearCoverage.length;
    const completeCoverage = sorted.filter((d) => d.coveragePct === 100).length;

    return {
      matrix: mat,
      yearLabels: years,
      sortedData: sorted,
      stats: {
        totalYears,
        avgCoverage: Math.round(avgCoverage * 10) / 10,
        bestYear,
        worstYear,
        completeCoverage,
        totalInitiatives: sorted.length,
      },
    };
  }, [data, locale]);

  if (!stats || sortedData.length === 0) {
    return (
      <div className="py-8 text-center text-fg-muted">
        {t('noCoverageData')}
      </div>
    );
  }

  const heatHeight = Math.max(400, sortedData.length * 25);

  const heatData: Data = {
    z: matrix,
    x: yearLabels,
    y: sortedData.map((d) => d.displayName),
    type: 'heatmap',
    colorscale: [
      [0, 'rgba(239,239,239,0.8)'],
      [1, 'rgba(76,175,80,0.8)'],
    ],
    showscale: false,
    hovertemplate: `<b>%{y}</b><br>${t('year')}: %{x}<br>${t('available')}: %{z}<extra></extra>`,
  };

  const barTrace: Data = {
    x: sortedData.map((d) => d.displayName),
    y: sortedData.map((d) => d.coveragePct),
    type: 'bar',
    marker: {
      color: sortedData.map((d) =>
        d.coveragePct >= 80 ? 'rgba(76,175,80,0.8)' :
        d.coveragePct >= 50 ? 'rgba(255,193,7,0.8)' :
        'rgba(239,83,80,0.8)',
      ),
    },
    text: sortedData.map((d) => `${d.coveragePct}%`),
    textposition: 'outside',
    hovertemplate: `<b>%{x}</b><br>${t('coverage')}: %{y}%<extra></extra>`,
  };

  return (
    <div className="space-y-6">
      <p className="text-sm text-fg-secondary">
        {tBody('coverageIntro')}
      </p>

      {/* Stats cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: t('avgCoveragePerYear'), value: `${stats.avgCoverage} ${t('initiativesUnit')}` },
          { label: t('bestCoveredYear'), value: `${stats.bestYear.year} (${stats.bestYear.count})` },
          { label: t('worstCoveredYear'), value: `${stats.worstYear.year} (${stats.worstYear.count})` },
          { label: t('completeCoverage'), value: `${stats.completeCoverage}/${stats.totalInitiatives}` },
        ].map((stat) => (
          <div key={stat.label} className="bg-surface rounded-lg border border-border p-3 text-center">
            <div className="text-xs text-fg-secondary mb-1">{stat.label}</div>
            <div className="text-sm font-semibold text-fg">{stat.value}</div>
          </div>
        ))}
      </div>

      {/* Coverage Heatmap */}
      <BaseChart
        data={[heatData]}
        layout={{
          title: { text: t('temporalCoverageMatrix'), x: 0 },
          xaxis: { title: t('year'), dtick: Math.max(1, Math.floor((yearLabels.length) / 20)) },
          yaxis: { title: '', autorange: 'reversed' },
          height: heatHeight,
          margin: { l: 150, r: 20, t: 40, b: 60 },
        }}
      />

      {/* Coverage Percentage Bar Chart */}
      <BaseChart
        data={[barTrace]}
        layout={{
          title: { text: t('coverageByInitiative'), x: 0 },
          xaxis: { title: '' },
          yaxis: { title: t('coveragePct'), range: [0, 105] },
          height: Math.max(350, sortedData.length * 30),
          margin: { l: 50, r: 20, t: 40, b: 120 },
        }}
      />
    </div>
  );
}
