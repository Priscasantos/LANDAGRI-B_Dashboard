import type { ReactElement, ReactNode } from 'react';

export interface SplitPane {
  /** Pane heading — also the section's accessible name. */
  title: string;
  /** Initiative/year selector rendered above the chart. */
  selector: ReactNode;
  /** The ECharts chart (both panes share one `group` id for sync). */
  chart: ReactNode;
}

interface SplitCompareViewProps {
  paneA: SplitPane;
  paneB: SplitPane;
}

/**
 * Split-view layout (Expansão #4, reversível): two labelled panes side by
 * side on desktop, stacked mobile-first. Tooltip/zoom sync comes from the
 * shared ECharts `group` id on each chart (`EChartsBase` → `connect`).
 *
 * Follow-up (fora do escopo, documentado): split de mapas — 2
 * `MapContainer` sincronizados (mesmos bounds/eventos). Não implementado:
 * o split de charts acima cobre o comparativo sem duplicar o custo do
 * Leaflet nem quebrar as rotas do módulo.
 */
export default function SplitCompareView({
  paneA,
  paneB,
}: SplitCompareViewProps): ReactElement {
  const panes: SplitPane[] = [paneA, paneB];
  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
      {panes.map((pane, index) => (
        <section
          key={index === 0 ? 'pane-a' : 'pane-b'}
          aria-label={pane.title}
          className="min-w-0"
        >
          <h3 className="text-base font-semibold text-fg mb-2">{pane.title}</h3>
          {pane.selector}
          {pane.chart}
        </section>
      ))}
    </div>
  );
}
