import type { ReactElement } from 'react';
import {
  ResponsiveContainer,
  BarChart as RcBarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import {
  CHART_GRID_STROKE,
  CHART_TICK_FILL,
  CHART_TOOLTIP_STYLE,
  CHART_TOOLTIP_LABEL_STYLE,
  paletteColor,
} from './chartTheme';

export interface RechartsBarDatum {
  category: string;
  value: number;
  color?: string;
}

interface RechartsBarChartProps {
  title: string;
  data: RechartsBarDatum[];
  xlabel?: string;
  ylabel?: string;
  height?: number;
  layout?: 'vertical' | 'horizontal';
}

/**
 * shadcn-style bar chart (área colhida média, IBGE/CONAB).
 * Accessible: `role="img"` + `aria-label` + keyboard focus.
 */
export function RechartsBarChart({
  title,
  data,
  height = 350,
  layout = 'horizontal',
}: RechartsBarChartProps): ReactElement {
  return (
    <figure
      role="img"
      aria-label={title}
      tabIndex={0}
      className="w-full rounded-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
    >
      <figcaption className="sr-only">
        {title}. {data.map((d) => `${d.category}: ${d.value}`).join('; ')}.
      </figcaption>
      <div style={{ width: '100%', height }} aria-hidden="true">
        <ResponsiveContainer width="100%" height="100%">
          <RcBarChart
            data={data}
            layout={layout === 'vertical' ? 'vertical' : 'horizontal'}
            margin={{ top: 10, right: 20, left: 0, bottom: 60 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke={CHART_GRID_STROKE} vertical={false} />
            {layout === 'vertical' ? (
              <>
                <XAxis type="number" tick={{ fontSize: 11, fill: CHART_TICK_FILL }} />
                <YAxis type="category" dataKey="category" tick={{ fontSize: 11, fill: CHART_TICK_FILL }} width={110} />
              </>
            ) : (
              <>
                <XAxis dataKey="category" tick={{ fontSize: 11, fill: CHART_TICK_FILL }} angle={-45} textAnchor="end" height={70} interval={0} />
                <YAxis tick={{ fontSize: 11, fill: CHART_TICK_FILL }} tickLine={false} axisLine={false} />
              </>
            )}
            <Tooltip contentStyle={CHART_TOOLTIP_STYLE} labelStyle={CHART_TOOLTIP_LABEL_STYLE} />
            <Bar dataKey="value" name="Valor" radius={[6, 6, 0, 0]}>
              {data.map((d, i) => (
                <Cell key={d.category} fill={paletteColor(i, d.color)} />
              ))}
            </Bar>
          </RcBarChart>
        </ResponsiveContainer>
      </div>
    </figure>
  );
}
