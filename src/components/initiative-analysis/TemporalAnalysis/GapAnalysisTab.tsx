import { useMemo } from 'react';
import { Circle } from 'lucide-react';
import EChartsGroupedBar from '../../charts/echarts/EChartsGroupedBar';
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

interface GapAnalysisTabProps {
  data: TemporalData[];
}

/**
 * Largest temporal gap bars + average line — ECharts edition (Fase 2 fatia 2c).
 * Replaces the Plotly `BaseChart` bar/avg-line; gap math, legend, i18n and
 * chrome unchanged. Reversible: previous version in git history.
 */
export default function GapAnalysisTab({ data }: GapAnalysisTabProps) {
  const { t } = useT('charts');
  const { t: tBody } = useT('initiative');
  const gapData = useMemo(() => {
    if (data.length === 0) return [];

    return data
      .map((d) => {
        const sorted = [...d.years].sort((a, b) => a - b);
        let maxGap = 0;
        for (let i = 1; i < sorted.length; i++) {
          const gap = sorted[i] - sorted[i - 1] - 1;
          if (gap > maxGap) maxGap = gap;
        }
        return {
          name: d.displayName,
          acronym: d.name,
          maxGap,
          years: d.years,
          coveragePct: d.coveragePct,
        };
      })
      .sort((a, b) => b.maxGap - a.maxGap);
  }, [data]);

  if (gapData.length === 0) {
    return (
      <div className="py-8 text-center text-fg-muted">
        {tBody('noGapData')}
      </div>
    );
  }

  const avgGap = gapData.reduce((s, d) => s + d.maxGap, 0) / gapData.length;

  return (
    <div className="space-y-4">
      <p className="text-sm text-fg-secondary">
        {tBody('gapIntro')}
      </p>

      <EChartsGroupedBar
        categories={gapData.map((d) => d.name)}
        series={[{ name: t('largestGap'), values: gapData.map((d) => d.maxGap) }]}
        captionKey="largestTemporalGap"
        height={500}
        referenceLine={{
          value: avgGap,
          name: `${t('averageGap')} (${avgGap.toFixed(1)}${t('yearShort')})`,
          color: '#64748b',
        }}
      />

      {/* Color legend */}
      <div className="flex flex-wrap gap-4 justify-center text-xs text-fg-secondary">
        <span className="inline-flex items-center gap-1"><Circle size={10} aria-hidden="true" className="fill-green-500 text-green-500" /> {t('noGaps')}</span>
        <span className="inline-flex items-center gap-1"><Circle size={10} aria-hidden="true" className="fill-yellow-400 text-yellow-400" /> {t('smallGap')}</span>
        <span className="inline-flex items-center gap-1"><Circle size={10} aria-hidden="true" className="fill-orange-500 text-orange-500" /> {t('mediumGap')}</span>
        <span className="inline-flex items-center gap-1"><Circle size={10} aria-hidden="true" className="fill-red-500 text-red-500" /> {t('largeGap')}</span>
      </div>
    </div>
  );
}
