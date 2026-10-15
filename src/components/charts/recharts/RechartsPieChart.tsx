import type { ReactElement } from 'react';
import { ResponsiveContainer, PieChart as RcPieChart, Pie, Cell, Tooltip, Legend } from 'recharts';
import {
  CHART_TOOLTIP_STYLE,
  CHART_TOOLTIP_LABEL_STYLE,
  formatTickValue,
  paletteColor,
} from './chartTheme';
import { useT } from '../../../i18n/LanguageContext';

export interface RechartsPieSlice {
  label: string;
  value: number;
  color?: string;
}

interface RechartsPieChartProps {
  title: string;
  data: RechartsPieSlice[];
  height?: number;
  donut?: boolean;
}

/**
 * shadcn-style pie/donut chart (distribuição da produção, IBGE/CONAB).
 * Accessible: `role="img"` + `aria-label` + keyboard focus.
 */
export function RechartsPieChart({
  title,
  data,
  height = 350,
  donut = true,
}: RechartsPieChartProps): ReactElement {
  const { locale } = useT('charts');
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
        {title}. {data.map((d) => `${d.label}: ${formatTickValue(d.value, locale)}`).join('; ')}.
      </figcaption>
      <div style={{ width: '100%', minWidth: 0, height }} aria-hidden="true" className="min-w-0">
        <ResponsiveContainer width="100%" height={height} minWidth={0}>
          <RcPieChart>
            <Tooltip contentStyle={CHART_TOOLTIP_STYLE} labelStyle={CHART_TOOLTIP_LABEL_STYLE} formatter={valueTip} />
            <Legend
              iconType="square"
              iconSize={8}
              align="center"
              verticalAlign="bottom"
              wrapperStyle={{ fontSize: '11px', maxWidth: '100%', lineHeight: '16px', gap: '8px 15px' }}
            />
            <Pie
              data={data}
              dataKey="value"
              nameKey="label"
              innerRadius={donut ? '40%' : 0}
              outerRadius="75%"
              paddingAngle={2}
              labelLine={false}
            >
              {data.map((d, i) => (
                <Cell key={d.label} fill={paletteColor(i, d.color)} stroke="#fff" strokeWidth={2} />
              ))}
            </Pie>
          </RcPieChart>
        </ResponsiveContainer>
      </div>
    </figure>
  );
}
