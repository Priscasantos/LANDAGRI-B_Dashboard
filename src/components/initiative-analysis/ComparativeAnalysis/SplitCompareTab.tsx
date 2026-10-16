import { useMemo, useState, type ReactElement } from 'react';
import EChartsScatter from '../../charts/echarts/EChartsScatter';
import type { ScatterSeriesInput } from '../../charts/echarts/echarts-options';
import { useDashboardStore } from '../../../stores/dashboardStore';
import type { InitiativeRow } from '../../../types/initiative';
import { getInitiativeShortName } from '../../../data/glossary';
import { useT } from '../../../i18n/LanguageContext';
import type { Locale } from '../../../i18n/types';
import Select from '../../ui/Select';
import SplitCompareView from './SplitCompareView';

/** Shared ECharts group id — tooltips/zoom stay synchronized across panes. */
export const SPLIT_COMPARE_GROUP = 'landagri-split-compare';

type SplitMode = 'initiative' | 'year';

function toBubble(row: InitiativeRow, locale: Locale): ScatterSeriesInput {
  const name = getInitiativeShortName(row.Display_Name, locale);
  return {
    name,
    data: [[row.Accuracy, row.Resolution]],
    sizes: [row.Number_of_Classes],
    labels: [name],
  };
}

function validRows(rows: InitiativeRow[]): InitiativeRow[] {
  return rows.filter(
    (i) => i.Accuracy > 0 && i.Resolution > 0 && i.Number_of_Classes > 0,
  );
}

/**
 * Split compare tab (Expansão #4, reversível): same scatter (accuracy vs
 * resolution, bubble = class count) on both sides, A/B selectors by
 * initiative (same `Name (Acronym)` options as `InitiativeSelector`) or by
 * year. Panes sync via `SPLIT_COMPARE_GROUP`. Reversible: remove the tab
 * entry in `ComparativePage` to roll back.
 */
export default function SplitCompareTab(): ReactElement {
  const { t: tBody, locale } = useT('initiative');
  const initiatives = useDashboardStore((s) => s.initiatives);
  const [mode, setMode] = useState<SplitMode>('initiative');
  const [selA, setSelA] = useState<string>('');
  const [selB, setSelB] = useState<string>('');

  const initiativeOptions = useMemo(
    () =>
      initiatives.map((i) => ({
        value: i.Name,
        label: getInitiativeShortName(i.Display_Name, locale),
      })),
    [initiatives, locale],
  );

  const years = useMemo(() => {
    const set = new Set<number>();
    initiatives.forEach((i) => i.Available_Years.forEach((y) => set.add(y)));
    return [...set].sort((a, b) => a - b);
  }, [initiatives]);
  const yearOptions = useMemo(
    () => years.map((y) => ({ value: String(y), label: String(y) })),
    [years],
  );

  // Effective selections default to the first options (no setState-in-effect:
  // derived during render so defaults follow async store hydration).
  const effA =
    selA !== ''
      ? selA
      : mode === 'initiative'
        ? (initiativeOptions[0]?.value ?? '')
        : years.length > 0
          ? String(years[0])
          : '';
  const effB =
    selB !== ''
      ? selB
      : mode === 'initiative'
        ? (initiativeOptions[1]?.value ?? initiativeOptions[0]?.value ?? '')
        : years.length > 0
          ? String(years[years.length - 1])
          : '';

  const { titleA, titleB, seriesA, seriesB } = useMemo(() => {
    if (mode === 'initiative') {
      const rowA = initiatives.find((i) => i.Name === effA);
      const rowB = initiatives.find((i) => i.Name === effB);
      return {
        titleA:
          rowA !== undefined ? getInitiativeShortName(rowA.Display_Name, locale) : tBody('splitInitiativeA'),
        titleB:
          rowB !== undefined ? getInitiativeShortName(rowB.Display_Name, locale) : tBody('splitInitiativeB'),
        seriesA: rowA !== undefined ? validRows([rowA]).map((r) => toBubble(r, locale)) : [],
        seriesB: rowB !== undefined ? validRows([rowB]).map((r) => toBubble(r, locale)) : [],
      };
    }
    const yearA = Number(effA);
    const yearB = Number(effB);
    return {
      titleA: effA === '' ? tBody('splitYearA') : effA,
      titleB: effB === '' ? tBody('splitYearB') : effB,
      seriesA: validRows(
        initiatives.filter((i) => i.Available_Years.includes(yearA)),
      ).map((r) => toBubble(r, locale)),
      seriesB: validRows(
        initiatives.filter((i) => i.Available_Years.includes(yearB)),
      ).map((r) => toBubble(r, locale)),
    };
  }, [mode, initiatives, effA, effB, locale, tBody]);

  if (initiatives.length === 0) {
    return <div className="py-8 text-center text-fg-muted">{tBody('noPairwiseData')}</div>;
  }

  const modes: { id: SplitMode; label: string }[] = [
    { id: 'initiative', label: tBody('splitByInitiative') },
    { id: 'year', label: tBody('splitByYear') },
  ];

  return (
    <div className="space-y-4">
      <p className="text-sm text-fg-secondary">{tBody('splitIntro')}</p>
      <div role="group" aria-label={tBody('splitModeLabel')} className="flex gap-2">
        {modes.map((m) => (
          <button
            key={m.id}
            type="button"
            aria-pressed={mode === m.id}
            onClick={() => {
              setMode(m.id);
              setSelA('');
              setSelB('');
            }}
            className={`rounded-lg border px-3 py-1.5 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${
              mode === m.id
                ? 'border-transparent text-white'
                : 'border-border bg-surface-alt text-fg-secondary hover:bg-surface-hover'
            }`}
            style={
              mode === m.id ? { backgroundColor: 'var(--color-primary)' } : undefined
            }
          >
            {m.label}
          </button>
        ))}
      </div>
      <SplitCompareView
        paneA={{
          title: titleA,
          selector:
            mode === 'initiative' ? (
              <Select
                label={tBody('splitInitiativeA')}
                options={initiativeOptions}
                value={effA}
                onChange={setSelA}
                placeholder={tBody('splitInitiativeA')}
              />
            ) : (
              <Select
                label={tBody('splitYearA')}
                options={yearOptions}
                value={effA}
                onChange={setSelA}
                placeholder={tBody('splitYearA')}
              />
            ),
          chart: (
            <EChartsScatter
              series={seriesA}
              captionKey="accuracyVsResolution"
              height={420}
              yAxisType="log"
              group={SPLIT_COMPARE_GROUP}
            />
          ),
        }}
        paneB={{
          title: titleB,
          selector:
            mode === 'initiative' ? (
              <Select
                label={tBody('splitInitiativeB')}
                options={initiativeOptions}
                value={effB}
                onChange={setSelB}
                placeholder={tBody('splitInitiativeB')}
              />
            ) : (
              <Select
                label={tBody('splitYearB')}
                options={yearOptions}
                value={effB}
                onChange={setSelB}
                placeholder={tBody('splitYearB')}
              />
            ),
          chart: (
            <EChartsScatter
              series={seriesB}
              captionKey="accuracyVsResolution"
              height={420}
              yAxisType="log"
              group={SPLIT_COMPARE_GROUP}
            />
          ),
        }}
      />
    </div>
  );
}
