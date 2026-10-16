import { useState, useMemo } from 'react';
import { BarChart3, Radar, Flame, ClipboardList, CalendarDays } from 'lucide-react';
import { useDashboardStore } from '../../../stores/dashboardStore';
import Tabs from '../../ui/Tabs';
import { useT } from '../../../i18n/LanguageContext';
import BarChartTab from './BarChartTab';
import RadarTab from './RadarTab';
import HeatmapTab from './HeatmapTab';
import DataDetailsTab from './DataDetailsTab';
import AnnualCoverageTab from './AnnualCoverageTab';

export default function DetailedPage() {
  const { t } = useT('initiative');
  const initiatives = useDashboardStore((s) => s.initiatives);

  const initiativeOptions = useMemo(
    () => initiatives.map((i) => ({ value: i.Name, label: i.Display_Name })),
    [initiatives],
  );

  // Default: first 3 initiatives
  const defaultSelected = useMemo(
    () => initiatives.slice(0, 3).map((i) => i.Name),
    [initiatives],
  );

  const [selected, setSelected] = useState<string[]>(defaultSelected);

  const toggleInitiative = (name: string) => {
    setSelected((prev) =>
      prev.includes(name) ? prev.filter((n) => n !== name) : [...prev, name],
    );
  };

  const tabs = [
    { id: 'bar', label: t('tabBar'), icon: BarChart3, content: <BarChartTab selectedInitiatives={selected} /> },
    { id: 'radar', label: t('tabRadar'), icon: Radar, content: <RadarTab selectedInitiatives={selected} /> },
    { id: 'heatmap', label: t('tabHeatmap'), icon: Flame, content: <HeatmapTab selectedInitiatives={selected} /> },
    { id: 'data', label: t('tabDataDetails'), icon: ClipboardList, content: <DataDetailsTab selectedInitiatives={selected} /> },
    { id: 'coverage', label: t('tabAnnualCoverage'), icon: CalendarDays, content: <AnnualCoverageTab selectedInitiatives={selected} /> },
  ];

  return (
    <div className="space-y-6">
      {/* Multi-select for initiatives */}
      <div>
        <label className="block text-sm font-medium text-fg mb-2">
          {t('selectToCompare')}
        </label>
        <div className="flex flex-wrap gap-2">
          {initiativeOptions.map((opt) => {
            const isSelected = selected.includes(opt.value);
            return (
              <button
                key={opt.value}
                onClick={() => toggleInitiative(opt.value)}
                className={`px-3 py-1.5 text-xs font-medium rounded-full border transition-all duration-200 ${
                  isSelected
                    ? 'bg-blue-50 border-blue-300 text-blue-700'
                    : 'bg-surface border-border text-fg-secondary hover:border-surface-alt'
                }`}
              >
                {opt.label}
              </button>
            );
          })}
        </div>
        <p className="text-xs text-fg-muted mt-1">
          {t('toggleHint', { count: selected.length })}
        </p>
      </div>

      <Tabs tabs={tabs} />
    </div>
  );
}
