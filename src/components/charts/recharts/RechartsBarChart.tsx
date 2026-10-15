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
  formatTickValue,
  paletteColor,
} from './chartTheme';
import { useT } from '../../../i18n/LanguageContext';

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
  // locale reativo: troca PT↔EN refaz ticks/tooltip/figcaption (Fase 2).
  const { t, locale } = useT('charts');
  const valueTick = (v: number): string => formatTickValue(v, locale);
  const valueTip = (v: unknown): string =>
    typeof v === 'number' ? formatTickValue(v, locale) : String(v ?? '');
  return (
    <figure
      role="img"
      aria-label={title}
      tabIndex={0}
      className="w-full min-w-0 rounded-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
    >
      <figcaption className="sr-only">
        {title}. {data.map((d) => `${d.category}: ${formatTickValue(d.value, locale)}`).join('; ')}.
      </figcaption>
      <div style={{ width: '100%', minWidth: 0, height }} aria-hidden="true" className="min-w-0">
        <ResponsiveContainer width="100%" height={height} minWidth={0}>
          <RcBarChart
            data={data}
            layout={layout === 'vertical' ? 'vertical' : 'horizontal'}
            margin={{ top: 10, right: 24, left: 8, bottom: 60 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke={CHART_GRID_STROKE} vertical={false} />
            {layout === 'vertical' ? (
              <>
                <XAxis type="number" tick={{ fontSize: 11, fill: CHART_TICK_FILL }} tickMargin={4} tickFormatter={valueTick} />
                <YAxis
                  type="category"
                  dataKey="category"
                  tick={{ fontSize: 11, fill: CHART_TICK_FILL }}
                  width={120}
                  tickMargin={4}
                />
              </>
            ) : (
              <>
                <XAxis dataKey="category" tick={{ fontSize: 11, fill: CHART_TICK_FILL }} angle={-45} textAnchor="end" height={70} interval={0} tickMargin={4} />
                <YAxis
                  tick={{ fontSize: 11, fill: CHART_TICK_FILL }}
                  tickLine={false}
                  axisLine={false}
                  width={52}
                  tickMargin={4}
                  tickFormatter={valueTick}
                />
              </>
            )}
            <Tooltip contentStyle={CHART_TOOLTIP_STYLE} labelStyle={CHART_TOOLTIP_LABEL_STYLE} formatter={valueTip} />
            <Bar dataKey="value" name={t('valueLabel')} radius={[6, 6, 0, 0]}>
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
