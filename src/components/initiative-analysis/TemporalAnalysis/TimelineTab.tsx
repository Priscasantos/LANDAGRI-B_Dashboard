import { useMemo } from 'react';
import EChartsTimeline from '../../charts/echarts/EChartsTimeline';
import { getInitiativeShortName, translateMethodology, translateTerm } from '../../../data/glossary';
import { useT } from '../../../i18n/LanguageContext';

interface TemporalData {
  name: string;
  displayName: string;
  firstYear: number;
  lastYear: number;
  years: number[];
  coverageYears: number;
  totalPeriod: number;
  coveragePct: number;
  methodology: string;
  coverage: string;
}

interface TimelineTabProps {
  data: TemporalData[];
}

/**
 * Initiative timeline — ECharts edition (Fase 2 fatia 2c).
 * Replaces the Plotly `BaseChart` scatter+line timeline; data, sorting,
 * i18n and chrome unchanged. Reversible: previous version in git history.
 */
export default function TimelineTab({ data }: TimelineTabProps) {
  const { t, locale } = useT('charts');
  const { t: tBody } = useT('initiative');
  const sortedData = useMemo(
    () => [...data].sort((a, b) => {
      const covOrder = ['Global', 'Regional', 'National', 'Other'];
      const aIdx = covOrder.indexOf(a.coverage);
      const bIdx = covOrder.indexOf(b.coverage);
      if (aIdx !== bIdx) return aIdx - bIdx;
      return a.firstYear - b.firstYear;
    }),
    [data],
  );

  const height = Math.max(520, sortedData.length * 32);

  const items = useMemo(
    () =>
      sortedData.map((item) => ({
        label: getInitiativeShortName(item.displayName, locale),
        years: item.years,
        tip: (year: number): string =>
          `<b>${getInitiativeShortName(item.displayName, locale)}</b><br>${t('year')}: ${year}<br>${t('coverage')}: ${translateTerm('coverage', item.coverage, locale)}<br>${t('methodology')}: ${translateMethodology(item.methodology, locale)}`,
      })),
    [sortedData, t, locale],
  );

  return (
    <div className="space-y-4 min-w-0">
      <p className="text-sm text-fg-secondary">
        {tBody('timelineIntro')}
      </p>
      <EChartsTimeline
        items={items}
        captionKey="initiativeTimeline"
        height={height}
      />
      <p className="text-sm text-fg-secondary">
        {tBody('timelineAnimatedIntro')}
      </p>
      <EChartsTimeline
        items={items}
        captionKey="initiativeTimeline"
        height={height}
        animated
      />
    </div>
  );
}
