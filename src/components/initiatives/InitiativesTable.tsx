import { useMemo, type ReactElement } from 'react';
import { Download } from 'lucide-react';
import DataTable from '../ui/DataTable';
import { useDashboardStore } from '../../stores/dashboardStore';
import { getInitiativeShortName } from '../../data/glossary';
import { useT } from '../../i18n/LanguageContext';
import { useChartExport } from '../../hooks/use-chart-export';

interface InitiativesTableProps {
  className?: string;
  /** Route slug for the CSV filename (default `overview`). */
  route?: string;
  /** Highlighted initiative for the CSV filename. */
  initiative?: string;
}

/**
 * InitiativesTable — Fase 2 focused initiatives table
 * (colunas iniciativa/área/ano + resolução/acurácia).
 *
 * Lightweight wrapper over the existing `DataTable` (sort/search/paginate)
 * — no new dependency. NOTE (blocker registrado): the TanStack `data-table`
 * from `ref-shadcn-dashboard` targets the v9-beta `tableFeatures` API, which
 * is incompatible with the stable `@tanstack/react-table` v8 line; adopting
 * it would add a new dep + a beta API surface. Revisit when the template
 * lands on stable v8. Reversible: pure wrapper.
 *
 * Expansão #2 (reversível): CSV export button (papaparse) with
 * route/locale filename via `useChartExport`.
 */
export default function InitiativesTable({
  className = '',
  route = 'overview',
  initiative,
}: InitiativesTableProps): ReactElement {
  const { t, locale } = useT('overview');
  const { t: tTables } = useT('tables');
  const initiatives = useDashboardStore((s) => s.initiatives);
  const { exportCsv } = useChartExport({ chartId: 'initiatives', route, initiative });

  const data = useMemo(
    () =>
      initiatives.map((i) => ({
        iniciativa: getInitiativeShortName(i.Display_Name, locale),
        cobertura: i.Coverage,
        inicio: i.Year_Start,
        fim: i.Year_End,
        anos: i.Available_Years.length,
        periodo: i.Available_Years.length > 0 ? `${i.Year_Start}–${i.Year_End}` : '-',
        resolucao: i.Resolution,
        acuracia: i.Accuracy,
      })),
    [initiatives, locale],
  );

  const columns = useMemo(
    () => [
      { key: 'iniciativa', label: t('colInitiative') },
      { key: 'cobertura', label: t('colCoverage') },
      { key: 'periodo', label: t('colPeriod') },
      {
        key: 'resolucao',
        label: t('colResolution'),
        format: (v: unknown): string => (typeof v === 'number' && v > 0 ? `${v}m` : '-'),
      },
      {
        key: 'acuracia',
        label: t('colAccuracy'),
        format: (v: unknown): string =>
          typeof v === 'number' && v > 0 ? `${v.toFixed(1)}%` : '-',
      },
    ],
    [t],
  );

  if (initiatives.length === 0) {
    return (
      <p className="text-sm text-fg-muted py-8 text-center" role="status">
        {t('noInitiatives')}
      </p>
    );
  }

  const exportLabel = tTables('exportCsv');

  return (
    <div className={className}>
      <div className="mb-3 flex justify-end">
        <button
          type="button"
          onClick={() =>
            exportCsv(
              data.map((row) =>
                Object.fromEntries(
                  columns.map((col) => [col.label, row[col.key as keyof typeof row] ?? '']),
                ),
              )
            )
          }
          aria-label={exportLabel}
          className="inline-flex items-center gap-1.5 rounded-lg border border-border bg-surface-alt px-2.5 py-1.5 text-xs font-medium text-fg-secondary transition-colors hover:bg-surface-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
        >
          <Download size={14} aria-hidden="true" />
          {exportLabel}
        </button>
      </div>
      <DataTable columns={columns} data={data} searchable pageSize={10} />
    </div>
  );
}
