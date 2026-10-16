import { useMemo } from 'react';
import EChartsGantt from '../../charts/echarts/EChartsGantt';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { getInitiativeShortName } from '../../../data/glossary';
import { useT } from '../../../i18n/LanguageContext';

interface AnnualCoverageTabProps {
  selectedInitiatives: string[];
}

/**
 * Annual coverage periods — ECharts Gantt edition (Fase 2 fatia 2c).
 * Replaces the Plotly `base`-bar timeline; period math, i18n and chrome
 * unchanged. Reversible: previous version in git history.
 */
export default function AnnualCoverageTab({ selectedInitiatives }: AnnualCoverageTabProps) {
  const { t, locale } = useT('charts');
  const { t: tBody } = useT('initiative');
  const initiatives = useDashboardStore((s) => s.initiatives);

  const { bars, xLabels } = useMemo(() => {
    const filtered = initiatives
      .filter((i) => selectedInitiatives.includes(i.Name))
      .filter((i) => i.Available_Years.length > 0);

    if (filtered.length === 0) {
      return { bars: [], xLabels: [] as number[] };
    }

    const allYrs = new Set<number>();
    filtered.forEach((i) => i.Available_Years.forEach((y) => allYrs.add(y)));
    const rangeMin = Math.min(...allYrs) - 1;
    const rangeMax = Math.max(...allYrs) + 1;
    const labels: number[] = [];
    for (let y = rangeMin; y <= rangeMax; y++) labels.push(y);

    const b = filtered.map((i) => {
      const short = getInitiativeShortName(i.Display_Name, locale);
      const sortedYrs = [...i.Available_Years].sort((a, b) => a - b);
      const start = sortedYrs[0];
      const end = sortedYrs[sortedYrs.length - 1];
      return {
        label: short,
        start: start - rangeMin,
        end: end - rangeMin + 1,
        tip: `<b>${short}</b><br>${t('period')}: ${start} – ${end}`,
      };
    });

    return { bars: b, xLabels: labels };
  }, [initiatives, selectedInitiatives, t, locale]);

  if (bars.length === 0) {
    return (
      <div className="py-8 text-center text-fg-muted">
        {tBody('noSelectionAnnual')}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-fg-secondary">
        {tBody('annualIntro')}
      </p>
      <EChartsGantt
        xLabels={xLabels}
        bars={bars}
        captionKey="annualCoverageTimeline"
        height={Math.max(300, bars.length * 50)}
      />
    </div>
  );
}
