import { useMemo, type ReactElement } from 'react';
import { Target, Satellite, Tags, CalendarDays } from 'lucide-react';
import { useDashboardStore } from '../../stores/dashboardStore';
import SectionCards from '../ui/SectionCards';
import type { SectionCardItem } from '../ui/SectionCards';
import { formatNumber } from '../../lib/normalize';
import { averageOverValid, countValid, formatAccuracyPct } from '../../lib/accuracyDisplay';
import { translateTerm } from '../../data/glossary';
import { useT } from '../../i18n/LanguageContext';

/**
 * Summary cards — Fase 2: layout via `SectionCards` (overview variant),
 * conteúdo agro preservado (IBGE/CONAB/MapBiomas). Emojis decorativos
 * trocados por ícones Lucide com `aria-hidden` para leitores de tela.
 */
export default function SummaryCards(): ReactElement | null {
  const { t, locale } = useT('overview');
  const { t: tInitiative } = useT('initiative');
  const initiatives = useDashboardStore((s) => s.initiatives);

  const sections = useMemo((): { coverage: SectionCardItem[]; perf: SectionCardItem[] } | null => {
    if (initiatives.length === 0) return null;

    const totalInitiatives = initiatives.length;
    // Overall_Score (council): exclui fontes sem OA publicado (0 interno);
    // média sobre N válido, nunca diluída por ausentes.
    const accuracies = initiatives.map((i) => i.Accuracy);
    const validN = countValid(accuracies);
    const avgAccuracy = averageOverValid(accuracies);
    const avgAccuracyDisplay = validN > 0 ? `${avgAccuracy.toFixed(1)}%` : formatAccuracyPct(0);
    const avgResolution = initiatives.reduce((sum, i) => sum + i.Resolution, 0) / totalInitiatives;
    const totalClasses = initiatives.reduce((sum, i) => sum + i.Number_of_Classes, 0);
    const totalYears = new Set(initiatives.flatMap((i) => i.Available_Years)).size;

    const coverageCounts: Record<string, number> = {};
    initiatives.forEach((i) => {
      coverageCounts[i.Coverage] = (coverageCounts[i.Coverage] || 0) + 1;
    });

    const coverage: SectionCardItem[] = Object.entries(coverageCounts).map(([coverageName, count]) => ({
      key: coverageName,
      label: translateTerm('coverage', coverageName, locale),
      value: String(count),
      hint: t('ofTotal', { pct: ((count / totalInitiatives) * 100).toFixed(0) }),
    }));

    const perf: SectionCardItem[] = [
      {
        key: 'accuracy',
        Icon: Target,
        label: t('perfAccuracy'),
        value: avgAccuracyDisplay,
        hint: tInitiative('overallScoreNote'),
      },
      { key: 'resolution', Icon: Satellite, label: t('perfResolution'), value: `${avgResolution.toFixed(0)}m` },
      { key: 'classes', Icon: Tags, label: t('perfClasses'), value: formatNumber(totalClasses) },
      { key: 'years', Icon: CalendarDays, label: t('perfYears'), value: t('yearsUnit', { count: totalYears }) },
    ];

    return { coverage, perf };
  }, [initiatives, t, tInitiative, locale]);

  if (!sections) return null;

  return (
    <div className="space-y-6">
      <SectionCards variant="overview" title={t('titleCoverage')} items={sections.coverage} />
      <SectionCards variant="overview" title={t('titlePerf')} items={sections.perf} />
    </div>
  );
}
