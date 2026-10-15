import { useMemo, type ReactElement } from 'react';
import ReactEChartsCore from 'echarts-for-react/esm/core';
import type { EChartsCoreOption } from 'echarts/core';
import { echarts } from './echarts-setup';
import { echartsThemeName, type EChartsPilotTheme } from '../../../lib/echarts-theme';
import { useEffectiveTheme } from '../../../hooks/use-theme';

interface EChartsBaseProps {
  /** Pure ECharts option (from `echarts-options` builders). */
  option: EChartsCoreOption;
  /** Accessible name — `t('charts:…')` caption from the caller. */
  ariaLabel: string;
  /** Visible caption rendered as `<figcaption>`. */
  caption?: string;
  height?: number;
  className?: string;
}

/**
 * ECharts shell (pilot): SVG renderer, theme via `useEffectiveTheme`,
 * `role="img"` + `aria-label` + `<figcaption>` for a11y.
 */
export default function EChartsBase({
  option,
  ariaLabel,
  caption,
  height = 400,
  className = '',
}: EChartsBaseProps): ReactElement {
  const effective: EChartsPilotTheme = useEffectiveTheme();
  const themeName = echartsThemeName(effective);
  const merged = useMemo<EChartsCoreOption>(
    () => ({ ...option } as EChartsCoreOption),
    [option],
  );

  return (
    <figure className="w-full min-w-0">
      <ReactEChartsCore
        echarts={echarts}
        option={merged}
        theme={themeName}
        style={{ width: '100%', height, minHeight: Math.min(height, 350) }}
        className={`w-full min-w-0 ${className}`}
        opts={{ renderer: 'svg' }}
        aria-label={ariaLabel}
        role="img"
      />
      {caption !== undefined && caption !== '' ? (
        <figcaption className="sr-only">{caption}</figcaption>
      ) : null}
    </figure>
  );
}
