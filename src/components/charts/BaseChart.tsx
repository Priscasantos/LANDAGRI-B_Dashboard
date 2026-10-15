import { useEffect, useRef, useMemo, useState, type ReactElement } from 'react';
import type { Data, Layout, Config } from 'plotly.js';
import { buildStandardLayout, STANDARD_CONFIG, getChartLayout } from '../../lib/chartDefaults';
import { useEffectiveTheme } from '../../hooks/use-theme';

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
  const [loadError, setLoadError] = useState(false);

  const finalLayout = useMemo(() => {
    const base = useStandardLayout ? buildStandardLayout({ ...layout, height }) : { ...layout, height };
    const themeLayout = getChartLayout(theme);

    return {
      ...base,
      ...themeLayout,
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
    };
  }, [useStandardLayout, layout, height, theme]);

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
    <div className="w-full rounded-xl p-3 bg-surface border border-border">
      {loadError ? (
        <p role="alert" className="text-sm text-fg-secondary p-4 text-center">
          Não foi possível carregar o gráfico interativo. Tente recarregar a página.
        </p>
      ) : (
        <div
          ref={containerRef}
          role="img"
          aria-label={typeof layout?.title === 'object' ? layout.title.text : 'Gráfico interativo'}
          className={`w-full ${className}`}
          style={{ width: '100%', height: '100%', minHeight: '350px' }}
        />
      )}
    </div>
  );
}
