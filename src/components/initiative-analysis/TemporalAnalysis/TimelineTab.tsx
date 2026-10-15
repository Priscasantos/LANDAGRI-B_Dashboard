import { useMemo } from 'react';
import EChartsTimeline from '../../charts/echarts/EChartsTimeline';
import { CATEGORICAL_COLORS } from '../../../types/theme';
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
  const { t } = useT('charts');
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
      sortedData.map((item, idx) => ({
        label: item.displayName,
        years: item.years,
        color: CATEGORICAL_COLORS[idx % CATEGORICAL_COLORS.length],
        tip: (year: number): string =>
          `<b>${item.displayName}</b><br>${t('year')}: ${year}<br>${t('coverage')}: ${item.coverage}<br>${t('methodology')}: ${item.methodology}`,
      })),
    [sortedData, t],
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
    </div>
  );
}
