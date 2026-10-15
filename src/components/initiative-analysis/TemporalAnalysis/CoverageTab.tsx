import { useMemo } from 'react';
import EChartsHeatmap from '../../charts/echarts/EChartsHeatmap';
import EChartsGroupedBar from '../../charts/echarts/EChartsGroupedBar';
import { getInitiativeShortName } from '../../../data/glossary';
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

/**
 * Temporal coverage matrix + coverage bars — ECharts edition (Fase 2 fatia 2c).
 * Replaces the Plotly `BaseChart` heatmap/bar; stats cards, sorting, i18n
 * and chrome unchanged. Reversible: previous version in git history.
 */
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

      {/* Coverage Heatmap (0/1 binário; rampa sequencial do tema ativo) */}
      <EChartsHeatmap
        z={matrix}
        x={yearLabels}
        y={sortedData.map((d) => getInitiativeShortName(d.displayName, locale))}
        captionKey="temporalCoverageMatrix"
        height={heatHeight}
        min={0}
        max={1}
      />

      {/* Coverage Percentage Bar Chart */}
      <EChartsGroupedBar
        categories={sortedData.map((d) => getInitiativeShortName(d.displayName, locale))}
        series={[{ name: t('coveragePct'), values: sortedData.map((d) => d.coveragePct) }]}
        captionKey="coverageByInitiative"
        height={Math.max(350, sortedData.length * 30)}
      />
    </div>
  );
}
