import type { ReactElement } from 'react';
import {
  ResponsiveContainer,
  LineChart as RcLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import {
  CHART_GRID_STROKE,
  CHART_TICK_FILL,
  CHART_TOOLTIP_STYLE,
  CHART_TOOLTIP_LABEL_STYLE,
  paletteColor,
} from './chartTheme';

export interface RechartsPoint {
  x: string | number;
  y: number | null;
}

export interface RechartsLineSeries {
  name: string;
  data: RechartsPoint[];
  color?: string;
}

interface RechartsLineChartProps {
  title: string;
  series: RechartsLineSeries[];
  xlabel?: string;
  ylabel?: string;
  height?: number;
  showMarkers?: boolean;
}

type ChartRow = Record<string, string | number | null>;

/**
 * shadcn-style line chart (IBGE/CONAB evolution series).
 * Accessible: `role="img"` + `aria-label` + keyboard focus.
 */
export function RechartsLineChart({
  title,
  series,
  xlabel,
  ylabel,
  height = 350,
  showMarkers = true,
}: RechartsLineChartProps): ReactElement {
  const xValues = Array.from(new Set(series.flatMap((s) => s.data.map((p) => p.x)))).sort((a, b) =>
    a > b ? 1 : -1,
  );
  const rows: ChartRow[] = xValues.map((x) => {
    const row: ChartRow = { x };
    series.forEach((s) => {
      const point = s.data.find((p) => p.x === x);
      row[s.name] = point ? point.y : null;
    });
    return row;
  });

  return (
    <figure
      role="img"
      aria-label={title}
      tabIndex={0}
      className="w-full rounded-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
    >
      <figcaption className="sr-only">
        {title}
        {xlabel ? ` — ${xlabel}` : ''} {ylabel ? ` — ${ylabel}` : ''}.{' '}
        {series.map((s) => s.name).join(', ')}.
      </figcaption>
      <div style={{ width: '100%', height }} aria-hidden="true">
        <ResponsiveContainer width="100%" height="100%">
          <RcLineChart data={rows} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={CHART_GRID_STROKE} vertical={false} />
            <XAxis dataKey="x" tick={{ fontSize: 11, fill: CHART_TICK_FILL }} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: CHART_TICK_FILL }} tickLine={false} axisLine={false} />
            <Tooltip contentStyle={CHART_TOOLTIP_STYLE} labelStyle={CHART_TOOLTIP_LABEL_STYLE} />
            <Legend iconType="circle" wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
            {series.map((s, i) => (
              <Line
                key={s.name}
                type="monotone"
                name={s.name}
                dataKey={s.name}
                connectNulls
                stroke={paletteColor(i, s.color)}
                strokeWidth={2}
                dot={showMarkers ? { r: 3 } : false}
              />
            ))}
          </RcLineChart>
        </ResponsiveContainer>
      </div>
    </figure>
  );
}
