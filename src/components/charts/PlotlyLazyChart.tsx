import { lazy, Suspense, type ReactElement } from 'react';
import type { Data, Layout, Config } from 'plotly.js';
import DashboardSkeleton from '../ui/DashboardSkeleton';

const LazyBaseChart = lazy(() => import('./BaseChart'));

interface PlotlyLazyChartProps {
  data: Data[];
  layout?: Partial<Layout>;
  config?: Partial<Config>;
  height?: number;
  useStandardLayout?: boolean;
  className?: string;
}

/**
 * Route-level code-split wrapper for remaining plotly charts (Fase 2).
 * Keeps plotly in its isolated `plotly` chunk (see vite `manualChunks`) and
 * shows a skeleton while it loads. Prefer recharts wrappers for new charts.
 */
export default function PlotlyLazyChart(props: PlotlyLazyChartProps): ReactElement {
  return (
    <Suspense fallback={<DashboardSkeleton />}>
      <LazyBaseChart {...props} />
    </Suspense>
  );
}
