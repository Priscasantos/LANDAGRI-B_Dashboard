import type { ReactElement } from 'react';
import {
  ResponsiveContainer,
  AreaChart as RcAreaChart,
  Area,
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
import type { RechartsLineSeries } from './RechartsLineChart';

interface RechartsAreaChartProps {
  title: string;
  series: RechartsLineSeries[];
  height?: number;
  stacked?: boolean;
}

type ChartRow = Record<string, string | number | null>;

/**
 * shadcn-style area chart (séries acumuladas agro).
 * Accessible: `role="img"` + `aria-label` + keyboard focus.
 */
export function RechartsAreaChart({
  title,
  series,
  height = 350,
  stacked = false,
}: RechartsAreaChartProps): ReactElement {
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
      className="w-full min-w-0 rounded-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
    >
      <figcaption className="sr-only">
        {title}. {series.map((s) => s.name).join(', ')}.
      </figcaption>
      <div style={{ width: '100%', minWidth: 0, height }} aria-hidden="true" className="min-w-0">
        <ResponsiveContainer width="100%" height="100%" minWidth={0}>
          <RcAreaChart data={rows} margin={{ top: 10, right: 24, left: 8, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={CHART_GRID_STROKE} vertical={false} />
            <XAxis dataKey="x" tick={{ fontSize: 11, fill: CHART_TICK_FILL }} tickLine={false} tickMargin={4} />
            <YAxis
              tick={{ fontSize: 11, fill: CHART_TICK_FILL }}
              tickLine={false}
              axisLine={false}
              width={52}
              tickMargin={4}
            />
            <Tooltip contentStyle={CHART_TOOLTIP_STYLE} labelStyle={CHART_TOOLTIP_LABEL_STYLE} />
            <Legend
              iconType="square"
              iconSize={8}
              align="center"
              verticalAlign="bottom"
              wrapperStyle={{ fontSize: '11px', paddingTop: '10px', maxWidth: '100%', lineHeight: '16px', gap: '8px 15px' }}
            />
            {series.map((s, i) => (
              <Area
                key={s.name}
                type="monotone"
                name={s.name}
                dataKey={s.name}
                connectNulls
                stackId={stacked ? 'agro' : undefined}
                stroke={paletteColor(i, s.color)}
                fill={paletteColor(i, s.color)}
                fillOpacity={0.25}
                strokeWidth={2}
              />
            ))}
          </RcAreaChart>
        </ResponsiveContainer>
      </div>
    </figure>
  );
}
