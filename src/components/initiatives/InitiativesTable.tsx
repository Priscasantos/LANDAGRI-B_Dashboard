import { useMemo, type ReactElement } from 'react';
import DataTable from '../ui/DataTable';
import { useDashboardStore } from '../../stores/dashboardStore';
import { useT } from '../../i18n/LanguageContext';

interface InitiativesTableProps {
  className?: string;
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
 */
export default function InitiativesTable({ className = '' }: InitiativesTableProps): ReactElement {
  const { t } = useT('overview');
  const initiatives = useDashboardStore((s) => s.initiatives);

  const data = useMemo(
    () =>
      initiatives.map((i) => ({
        iniciativa: i.Display_Name,
        cobertura: i.Coverage,
        inicio: i.Year_Start,
        fim: i.Year_End,
        anos: i.Available_Years.length,
        periodo: i.Available_Years.length > 0 ? `${i.Year_Start}–${i.Year_End}` : '-',
        resolucao: i.Resolution,
        acuracia: i.Accuracy,
      })),
    [initiatives],
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

  return (
    <DataTable columns={columns} data={data} searchable className={className} pageSize={10} />
  );
}
