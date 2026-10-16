import { useState, useMemo, useEffect, startTransition } from 'react';
import { CalendarDays, Sun, Map } from 'lucide-react';
import Tabs from '../../ui/Tabs';
import CropCalendarFilters from './CropCalendarFilters';
import CalendarHeatmapsTab from './CalendarHeatmapsTab';
import ActivitiesTimelineTab from './ActivitiesTimelineTab';
import SpatioTemporalTab from './SpatioTemporalTab';
import SeasonalOverviewTab from './SeasonalOverviewTab';
import CropDistributionTab from './CropDistributionTab';
import MonthlyIntensityTab from './MonthlyIntensityTab';
import ActivityIntensityTab from './ActivityIntensityTab';
import conabMapping from '../../../data/processed/conab_mapping.json';
import { useT } from '../../../i18n/LanguageContext';

interface MappingDataType {
  crop_calendar?: Record<string, unknown[]>;
}

export default function CropCalendarPage() {
  const { t } = useT('agricultural');
  const mappingData = conabMapping as MappingDataType;
  const cropCalendar = mappingData?.crop_calendar;

  const crops = useMemo(() => {
    if (!cropCalendar) return [];
    return Object.keys(cropCalendar).sort();
  }, [cropCalendar]);

  const regions = ['North', 'Northeast', 'Central-West', 'Southeast', 'South'];

  const [selectedCrops, setSelectedCrops] = useState<string[]>(crops);
  const [selectedRegions, setSelectedRegions] = useState<string[]>(regions);

  // Sync selected crops when data loads (use startTransition to avoid cascading renders)
  useEffect(() => {
    if (crops.length > 0 && selectedCrops.length === 0) {
      startTransition(() => setSelectedCrops(crops));
    }
  }, [crops, selectedCrops.length]);

  const filterProps = {
    crops,
    regions,
    selectedCrops,
    selectedRegions,
    onCropsChange: setSelectedCrops,
    onRegionsChange: setSelectedRegions,
  };

  // P2a: 7 tabs reagrupadas em 3 seções (conteúdo preservado, só reagrupe visual).
  // Tabs são estado local (sem rotas internas) — nenhuma url/path muda.
  const calendarTabs = [
    {
      id: 'calendario',
      label: t('tabCalendar'),
      icon: CalendarDays,
      content: (
        <div className="space-y-8">
          <CalendarHeatmapsTab selectedCrops={selectedCrops} selectedRegions={selectedRegions} />
          <ActivitiesTimelineTab selectedCrops={selectedCrops} selectedRegions={selectedRegions} />
        </div>
      ),
    },
    {
      id: 'sazonalidade',
      label: t('tabSeasonality'),
      icon: Sun,
      content: (
        <div className="space-y-8">
          <SeasonalOverviewTab selectedCrops={selectedCrops} selectedRegions={selectedRegions} />
          <MonthlyIntensityTab selectedCrops={selectedCrops} selectedRegions={selectedRegions} />
          <ActivityIntensityTab selectedCrops={selectedCrops} selectedRegions={selectedRegions} />
        </div>
      ),
    },
    {
      id: 'territorio',
      label: t('tabTerritory'),
      icon: Map,
      content: (
        <div className="space-y-8">
          <SpatioTemporalTab selectedCrops={selectedCrops} selectedRegions={selectedRegions} />
          <CropDistributionTab selectedCrops={selectedCrops} selectedRegions={selectedRegions} />
        </div>
      ),
    },
  ];

  return (
    <div>
      <CropCalendarFilters {...filterProps} />
      <Tabs tabs={calendarTabs} />
    </div>
  );
}
