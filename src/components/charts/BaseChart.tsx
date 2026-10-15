import { useEffect, useRef, useMemo, useState, type ReactElement } from 'react';
import type { Data, Layout, Config } from 'plotly.js';
import { buildStandardLayout, STANDARD_CONFIG, getChartLayout, separatorsForLocale } from '../../lib/chartDefaults';
import { useEffectiveTheme } from '../../hooks/use-theme';
import { useChartFontFamily } from '../../hooks/use-chart-font';
import { useT } from '../../i18n/LanguageContext';

interface BaseChartProps {
  data: Data[];
  layout?: Partial<Layout>;
  config?: Partial<Config>;
  height?: number;
  useStandardLayout?: boolean;
  className?: string;
}

/**
 * Plotly chart shell with lazy-loaded `plotly.js-dist-min` (Fase 2).
 * The ~3MB plotly bundle is fetched via dynamic `import()` only when a
 * plotly chart actually mounts, so routes migrated to recharts (Overview,
 * Predictive) never download it. API unchanged — reversible.
 */
export default function BaseChart({
  data,
  layout,
  config,
  height = 400,
  useStandardLayout = true,
  className = '',
}: BaseChartProps): ReactElement {
  const containerRef = useRef<HTMLDivElement>(null);
  const theme = useEffectiveTheme();
  // Rebuild do layout em [theme, font, locale] (Fase 2): a fonte vem do
  // data-font reativo e o locale do provider (separators explícitos).
  const fontFamily = useChartFontFamily();
  const { t, locale } = useT('charts');
  const [loadError, setLoadError] = useState(false);

  const finalLayout = useMemo(() => {
    const base = useStandardLayout
      ? buildStandardLayout({ ...layout, height }, fontFamily)
      : { ...layout, height };
    const themeLayout = getChartLayout(theme, fontFamily);
    // Separador explícito do locale reativo (não só do <html lang>): o
    // toggle PT↔EN refaz o layout com `,.`/`.,` sem remontar o chart.
    const separators = separatorsForLocale(locale);

    return {
      ...base,
      ...themeLayout,
      separators,
      font: {
        ...base.font,
        ...themeLayout.font,
        ...layout?.font,
      },
      xaxis: {
        ...base.xaxis,
        ...themeLayout.xaxis,
        ...layout?.xaxis,
      },
      yaxis: {
        ...base.yaxis,
        ...themeLayout.yaxis,
        ...layout?.yaxis,
      },
      legend: {
        ...base.legend,
        ...themeLayout.legend,
        ...layout?.legend,
      },
      // `Layout.title` aceita `string | objeto`: normaliza para objeto
      // antes do spread (todos os chamadores passam `{ text, x }`).
      title: {
        ...(typeof base.title === 'object' ? base.title : {}),
        ...(typeof themeLayout.title === 'object' ? themeLayout.title : {}),
        ...(typeof layout?.title === 'object' ? layout.title : {}),
      },
    };
  }, [useStandardLayout, layout, height, theme, fontFamily, locale]);
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    let cancelled = false;
    let plotlyModule: typeof import('plotly.js-dist-min') | null = null;

    void import('plotly.js-dist-min')
      .then((mod) => {
        if (cancelled) return;
        plotlyModule = mod;
        const Plotly = mod.default ?? mod;
        void Plotly.react(container, data, finalLayout, {
          ...STANDARD_CONFIG,
          ...config,
        });
      })
      .catch((err: unknown) => {
        console.error('Failed to load plotly chart library:', err);
        if (!cancelled) setLoadError(true);
      });

    return () => {
      cancelled = true;
      if (container && plotlyModule) {
        const Plotly = plotlyModule.default ?? plotlyModule;
        Plotly.purge(container);
      }
    };
  }, [data, finalLayout, config]);

  return (
    <div className="w-full min-w-0 overflow-hidden rounded-xl p-3 bg-surface border border-border">
      {loadError ? (
        <p role="alert" className="text-sm text-fg-secondary p-4 text-center">
          {t('chartLoadError')}
        </p>
      ) : (
        <div
          ref={containerRef}
          role="img"
          aria-label={typeof layout?.title === 'object' ? layout.title.text : t('interactiveChart')}
          className={`w-full min-w-0 ${className}`}
          style={{ width: '100%', minWidth: 0, height, minHeight: Math.min(height, 350) }}
        />
      )}
    </div>
  );
}
