import { useMemo, type ReactElement } from 'react';
import ReactEChartsCore from 'echarts-for-react/esm/core';
import type { EChartsCoreOption } from 'echarts/core';
import { Download } from 'lucide-react';
import { echarts } from './echarts-setup';
import { echartsThemeName, type EChartsPilotTheme } from '../../../lib/echarts-theme';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { useChartExport, type ChartRow } from '../../../hooks/use-chart-export';

interface EChartsBaseProps {
  /** Pure ECharts option (from `echarts-options` builders). */
  option: EChartsCoreOption;
  /** Accessible name — `t('charts:…')` caption from the caller. */
  ariaLabel: string;
  /** Visible caption rendered as `<figcaption>`. */
  caption?: string;
  height?: number;
  className?: string;
  /** Chart id for the download filename (`landagri-{route}-{locale}-{chartId}`). */
  chartId?: string;
  /** Route slug for the download filename (default: current pathname). */
  route?: string;
  /** Highlighted initiative for the download filename. */
  initiative?: string;
  /**
   * Visible dataset for the CSV button. Omitted/empty → no button
   * (the builder toolbox still offers PNG + data view).
   */
  exportRows?: ChartRow[];
}

/**
 * ECharts shell (pilot): SVG renderer, theme via `useEffectiveTheme`,
 * `role="img"` + `aria-label` + `<figcaption>` for a11y. The figure is
 * keyboard-focusable with a visible ring (same contract as the retired
 * recharts wrappers).
 *
 * Expansão #2 (reversível): `toolbox.saveAsImage` name is overridden with
 * the route/initiative/locale stem, and a translated CSV button exports
 * `exportRows` (papaparse) when provided.
 */
export default function EChartsBase({
  option,
  ariaLabel,
  caption,
  height = 400,
  className = '',
  chartId,
  route,
  initiative,
  exportRows,
}: EChartsBaseProps): ReactElement {
  const effective: EChartsPilotTheme = useEffectiveTheme();
  const themeName = echartsThemeName(effective);
  const { fileStem, exportLabel, exportCsv } = useChartExport({
    chartId,
    route,
    initiative,
  });
  const merged = useMemo<EChartsCoreOption>(() => {
    const next = { ...(option as Record<string, unknown>) };
    const toolbox = next.toolbox as Record<string, unknown> | undefined;
    if (toolbox !== undefined) {
      const feature = (toolbox.feature ?? {}) as Record<string, unknown>;
      const saveAsImage = (feature.saveAsImage ?? {}) as Record<string, unknown>;
      next.toolbox = {
        ...toolbox,
        feature: { ...feature, saveAsImage: { ...saveAsImage, name: fileStem } },
      };
    }
    return next as EChartsCoreOption;
  }, [option, fileStem]);
  const showExport = exportRows !== undefined && exportRows.length > 0;

  return (
    <div className="w-full min-w-0">
      <figure
        role="img"
        aria-label={ariaLabel}
        tabIndex={0}
        className="landagri-chart w-full min-w-0 rounded-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
      >
        <ReactEChartsCore
          echarts={echarts}
          option={merged}
          theme={themeName}
          style={{ width: '100%', height, minHeight: Math.min(height, 350) }}
          className={`w-full min-w-0 ${className}`}
          opts={{ renderer: 'svg' }}
        />
        {caption !== undefined && caption !== '' ? (
          <figcaption className="sr-only">{caption}</figcaption>
        ) : null}
      </figure>
      {showExport ? (
        <div className="mt-2 flex justify-end">
          <button
            type="button"
            onClick={() => exportCsv(exportRows)}
            aria-label={exportLabel}
            className="inline-flex items-center gap-1.5 rounded-lg border border-border bg-surface-alt px-2.5 py-1.5 text-xs font-medium text-fg-secondary transition-colors hover:bg-surface-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
          >
            <Download size={14} aria-hidden="true" />
            {exportLabel}
          </button>
        </div>
      ) : null}
    </div>
  );
}
