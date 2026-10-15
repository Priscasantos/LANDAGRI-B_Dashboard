import { useMemo } from 'react';
import BaseChart from '../../charts/BaseChart';
import type { Data } from 'plotly.js';
import { CATEGORICAL_COLORS } from '../../../types/theme';

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

interface TimelineTabProps {
  data: TemporalData[];
}

export default function TimelineTab({ data }: TimelineTabProps) {
  const sortedData = useMemo(
    () => [...data].sort((a, b) => {
      const covOrder = ['Global', 'Regional', 'National', 'Other'];
      const aIdx = covOrder.indexOf(a.coverage);
      const bIdx = covOrder.indexOf(b.coverage);
      if (aIdx !== bIdx) return aIdx - bIdx;
      return a.firstYear - b.firstYear;
    }),
    [data],
  );

  const height = Math.max(520, sortedData.length * 32);

  const traces: Data[] = sortedData.map((item, idx) => {
    const color = CATEGORICAL_COLORS[idx % CATEGORICAL_COLORS.length];
    return {
      x: item.years,
      y: item.years.map(() => item.displayName),
      mode: 'markers',
      type: 'scatter',
      name: item.displayName,
      marker: {
        size: 12,
        color,
        line: { width: 2, color: 'white' },
        symbol: 'circle',
      },
      hovertemplate: `<b>${item.displayName}</b><br>Year: %{x}<br>Coverage: ${item.coverage}<br>Methodology: ${item.methodology}<extra></extra>`,
    };
  });

  // Add connecting lines
  const lineTraces: Data[] = sortedData.map((item, idx) => {
    const color = CATEGORICAL_COLORS[idx % CATEGORICAL_COLORS.length];
    return {
      x: [item.firstYear, item.lastYear],
      y: [item.displayName, item.displayName],
      mode: 'lines',
      type: 'scatter',
      name: `${item.displayName} period`,
      line: { color, width: 3, opacity: 0.5 },
      hoverinfo: 'skip',
      showlegend: false,
    };
  });

  const allYears = sortedData.flatMap((d) => d.years);
  const yearMin = Math.min(...allYears);
  const yearMax = Math.max(...allYears);

  return (
    <div className="space-y-4 min-w-0">
      <p className="text-sm text-fg-secondary">
        Timeline showing available years for each initiative. Each dot represents a year with data.
        Initiatives are sorted by coverage type (Global first), then by start year.
      </p>
      <BaseChart
        data={[...lineTraces, ...traces]}
        height={height}
        layout={{
          title: { text: 'Initiative Timeline', x: 0 },
          xaxis: {
            title: { text: 'Year' },
            range: [yearMin - 1, yearMax + 1],
            dtick: yearMax - yearMin > 40 ? 5 : 1,
            tickfont: { size: 11 },
            automargin: true,
          },
          yaxis: {
            title: { text: '' },
            autorange: 'reversed',
            tickfont: { size: 11 },
            automargin: true,
          },
          margin: { l: 180, r: 60, t: 60, b: 80 },
          height,
          showlegend: false,
          hovermode: 'closest',
        }}
      />
    </div>
  );
}
