import { useMemo } from 'react';
import DataTable from '../../ui/DataTable';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { translateMethodology, translateTerm } from '../../../data/glossary';
import { useT } from '../../../i18n/LanguageContext';

/**
 * Methodology × coverage — P2b: tabela em vez de grouped-bar sobre enum.
 * Contagens baixas (0–3) num gráfico de barras agrupadas sugerem precisão
 * que os dados não têm; a tabela sortable mostra o mesmo sem ruído.
 * P3: rótulos via glossário (coverage "Brazil"/"Brasil"→Nacional/National).
 * Reversível: versão com ECharts no histórico git.
 */
export default function MethodologyDistributionTab() {
  const { t: tBody } = useT('initiative');
  const { t: tCharts, locale } = useT('charts');
  const initiatives = useDashboardStore((s) => s.initiatives);

  const { coverageTypes, rows } = useMemo(() => {
    const methods = [...new Set(initiatives.map((i) => i.Methodology))].sort();
    const coverages = [...new Set(initiatives.map((i) => i.Coverage))].sort();

    const grouped: Record<string, Record<string, number>> = {};
    methods.forEach((m) => {
      grouped[m] = {};
      coverages.forEach((c) => {
        grouped[m][c] = 0;
      });
    });

    initiatives.forEach((i) => {
      if (grouped[i.Methodology] && grouped[i.Methodology][i.Coverage] !== undefined) {
        grouped[i.Methodology][i.Coverage]++;
      }
    });

    return {
      coverageTypes: coverages,
      rows: methods.map((m) => ({
        methodology: translateMethodology(m, locale),
        ...Object.fromEntries(coverages.map((c) => [c, grouped[m][c]])),
        total: coverages.reduce((sum, c) => sum + grouped[m][c], 0),
      })),
    };
  }, [initiatives, locale]);

  if (rows.length === 0) {
    return <div className="py-8 text-center text-fg-muted">{tBody('noMethodologyData')}</div>;
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-fg-secondary">{tBody('methodologyTableIntro')}</p>
      <DataTable
        columns={[
          { key: 'methodology', label: tCharts('methodology') },
          ...coverageTypes.map((c) => ({ key: c, label: translateTerm('coverage', c, locale) })),
          { key: 'total', label: tCharts('total') },
        ]}
        data={rows as unknown as Record<string, unknown>[]}
      />
    </div>
  );
}
