import { useMemo } from 'react';
import { Circle } from 'lucide-react';
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

interface GapAnalysisTabProps {
  data: TemporalData[];
}

export default function GapAnalysisTab({ data }: GapAnalysisTabProps) {
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

  const getGapColor = (gap: number) => {
    if (gap === 0) return 'rgba(76,175,80,0.8)';
    if (gap <= 2) return 'rgba(255,193,7,0.8)';
    if (gap <= 5) return 'rgba(255,152,0,0.8)';
    return 'rgba(244,67,54,0.8)';
  };

  if (gapData.length === 0) {
    return (
      <div className="py-8 text-center text-fg-muted">
        No gap analysis data available.
      </div>
    );
  }

  const avgGap = gapData.reduce((s, d) => s + d.maxGap, 0) / gapData.length;

  const barTrace: Data = {
    x: gapData.map((d) => d.name),
    y: gapData.map((d) => d.maxGap),
    type: 'bar',
    marker: {
      color: gapData.map((d) => getGapColor(d.maxGap)),
      line: { width: 1, color: 'white' },
    },
    text: gapData.map((d) => `${d.maxGap} year${d.maxGap !== 1 ? 's' : ''}`),
    textposition: 'outside',
    hovertemplate: '<b>%{x}</b><br>Largest Gap: %{y} year(s)<br>Coverage: %{customdata}%<extra></extra>',
    customdata: gapData.map((d) => d.coveragePct),
  };

  const avgGapTrace: Data = {
    x: [gapData[0]?.name || '', gapData[gapData.length - 1]?.name || ''],
    y: [avgGap, avgGap],
    type: 'scatter',
    mode: 'lines',
    name: `Average gap (${avgGap.toFixed(1)}y)`,
    line: { color: '#64748b', width: 2, dash: 'dash' },
    hoverinfo: 'skip',
  };

  return (
    <div className="space-y-4">
      <p className="text-sm text-fg-secondary">
        Analysis of the largest temporal gap (consecutive missing years) for each initiative.
        Gaps are color-coded by severity.
      </p>

      <BaseChart
        data={[barTrace, avgGapTrace]}
        layout={{
          title: { text: 'Largest Temporal Gap by Initiative', x: 0 },
          xaxis: { title: '' },
          yaxis: { title: 'Gap (years)', dtick: 1 },
          height: 500,
          margin: { l: 50, r: 20, t: 40, b: 120 },
          hovermode: 'closest',
        }}
      />

      {/* Color legend */}
      <div className="flex flex-wrap gap-4 justify-center text-xs text-fg-secondary">
        <span className="inline-flex items-center gap-1"><Circle size={10} aria-hidden="true" className="fill-green-500 text-green-500" /> No gaps</span>
        <span className="inline-flex items-center gap-1"><Circle size={10} aria-hidden="true" className="fill-yellow-400 text-yellow-400" /> Small (&le;2y)</span>
        <span className="inline-flex items-center gap-1"><Circle size={10} aria-hidden="true" className="fill-orange-500 text-orange-500" /> Medium (3-5y)</span>
        <span className="inline-flex items-center gap-1"><Circle size={10} aria-hidden="true" className="fill-red-500 text-red-500" /> Large (&gt;5y)</span>
      </div>
    </div>
  );
}
