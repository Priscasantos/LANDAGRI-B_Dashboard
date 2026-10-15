import { useMemo, type ReactElement } from 'react';
import { Target, Satellite, Tags, CalendarDays } from 'lucide-react';
import { useDashboardStore } from '../../stores/dashboardStore';
import Card from '../ui/Card';
import { formatNumber } from '../../lib/normalize';

/**
 * Summary cards — padrão shadcn Card (Fase 2), conteúdo agro preservado
 * (IBGE/CONAB/MapBiomas). Emojis decorativos trocados por ícones Lucide
 * com `aria-hidden` para leitores de tela.
 */
export default function SummaryCards(): ReactElement | null {
  const initiatives = useDashboardStore((s) => s.initiatives);

  const metrics = useMemo(() => {
    if (initiatives.length === 0) return null;

    const totalInitiatives = initiatives.length;
    const avgAccuracy = initiatives.reduce((sum, i) => sum + i.Accuracy, 0) / totalInitiatives;
    const avgResolution = initiatives.reduce((sum, i) => sum + i.Resolution, 0) / totalInitiatives;
    const totalClasses = initiatives.reduce((sum, i) => sum + i.Number_of_Classes, 0);
    const totalYears = new Set(initiatives.flatMap((i) => i.Available_Years)).size;

    const coverageCounts: Record<string, number> = {};
    initiatives.forEach((i) => {
      coverageCounts[i.Coverage] = (coverageCounts[i.Coverage] || 0) + 1;
    });

    return { totalInitiatives, avgAccuracy, avgResolution, totalClasses, totalYears, coverageCounts };
  }, [initiatives]);

  if (!metrics) return null;

  const { totalInitiatives, avgAccuracy, avgResolution, totalClasses, totalYears, coverageCounts } =
    metrics;

  const perfCards = [
    { icon: Target, label: 'Avg Accuracy', value: `${avgAccuracy.toFixed(1)}%` },
    { icon: Satellite, label: 'Avg Resolution', value: `${avgResolution.toFixed(0)}m` },
    { icon: Tags, label: 'Total Classes', value: formatNumber(totalClasses) },
    { icon: CalendarDays, label: 'Temporal Coverage', value: `${totalYears} years` },
  ];

  return (
    <div className="space-y-6">
      {/* Coverage distribution cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4" role="list" aria-label="Distribuição por cobertura">
        {Object.entries(coverageCounts).map(([coverage, count]) => (
          <Card key={coverage} padding="sm" title={`${coverage}: ${count} iniciativas`}>
            <div className="text-center" role="listitem">
              <div className="text-xs font-medium text-fg-secondary uppercase tracking-wider">
                {coverage}
              </div>
              <div className="text-2xl font-bold text-fg mt-1">{count}</div>
              <div className="text-xs text-fg-muted mt-0.5">
                {((count / totalInitiatives) * 100).toFixed(0)}% of total
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Performance metrics cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4" role="list" aria-label="Métricas de desempenho">
        {perfCards.map(({ icon: Icon, label, value }) => (
          <Card key={label} padding="sm" title={`${label}: ${value}`}>
            <div className="text-center" role="listitem">
              <Icon size={24} aria-hidden="true" className="mx-auto mb-1 text-fg-secondary" />
              <div className="text-xs font-medium text-fg-secondary">{label}</div>
              <div className="text-xl font-bold text-fg">{value}</div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
