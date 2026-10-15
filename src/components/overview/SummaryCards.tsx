import { useMemo, type ReactElement } from 'react';
import { Target, Satellite, Tags, CalendarDays } from 'lucide-react';
import { useDashboardStore } from '../../stores/dashboardStore';
import SectionCards from '../ui/SectionCards';
import type { SectionCardItem } from '../ui/SectionCards';
import { formatNumber } from '../../lib/normalize';

/**
 * Summary cards — Fase 2: layout via `SectionCards` (overview variant),
 * conteúdo agro preservado (IBGE/CONAB/MapBiomas). Emojis decorativos
 * trocados por ícones Lucide com `aria-hidden` para leitores de tela.
 */
export default function SummaryCards(): ReactElement | null {
  const initiatives = useDashboardStore((s) => s.initiatives);

  const sections = useMemo((): { coverage: SectionCardItem[]; perf: SectionCardItem[] } | null => {
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

    const coverage: SectionCardItem[] = Object.entries(coverageCounts).map(([coverageName, count]) => ({
      key: coverageName,
      label: coverageName,
      value: String(count),
      hint: `${((count / totalInitiatives) * 100).toFixed(0)}% of total`,
    }));

    const perf: SectionCardItem[] = [
      { key: 'accuracy', Icon: Target, label: 'Avg Accuracy', value: `${avgAccuracy.toFixed(1)}%` },
      { key: 'resolution', Icon: Satellite, label: 'Avg Resolution', value: `${avgResolution.toFixed(0)}m` },
      { key: 'classes', Icon: Tags, label: 'Total Classes', value: formatNumber(totalClasses) },
      { key: 'years', Icon: CalendarDays, label: 'Temporal Coverage', value: `${totalYears} years` },
    ];

    return { coverage, perf };
  }, [initiatives]);

  if (!sections) return null;

  return (
    <div className="space-y-6">
      <SectionCards variant="overview" title="Distribuição por cobertura" items={sections.coverage} />
      <SectionCards variant="overview" title="Métricas de desempenho" items={sections.perf} />
    </div>
  );
}
