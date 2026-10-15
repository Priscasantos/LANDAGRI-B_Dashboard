import { useState, useMemo, useEffect, startTransition } from 'react';
import { CalendarDays, History, Map, Sun, BarChart3, TrendingUp, Zap } from 'lucide-react';
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

  const calendarTabs = [
    {
      id: 'heatmaps',
      label: t('tabHeatmaps'),
      icon: CalendarDays,
      content: <CalendarHeatmapsTab selectedCrops={selectedCrops} selectedRegions={selectedRegions} />,
    },
    {
      id: 'timeline',
      label: t('tabActivitiesTimeline'),
      icon: History,
      content: <ActivitiesTimelineTab selectedCrops={selectedCrops} selectedRegions={selectedRegions} />,
    },
    {
      id: 'spatiotemporal',
      label: t('tabSpatioTemporal'),
      icon: Map,
      content: <SpatioTemporalTab selectedCrops={selectedCrops} selectedRegions={selectedRegions} />,
    },
    {
      id: 'seasonal',
      label: t('tabSeasonal'),
      icon: Sun,
      content: <SeasonalOverviewTab selectedCrops={selectedCrops} selectedRegions={selectedRegions} />,
    },
    {
      id: 'distribution',
      label: t('tabCropDistribution'),
      icon: BarChart3,
      content: <CropDistributionTab selectedCrops={selectedCrops} selectedRegions={selectedRegions} />,
    },
    {
      id: 'intensity',
      label: t('tabMonthly'),
      icon: TrendingUp,
      content: <MonthlyIntensityTab selectedCrops={selectedCrops} selectedRegions={selectedRegions} />,
    },
    {
      id: 'activity',
      label: t('tabActivity'),
      icon: Zap,
      content: <ActivityIntensityTab selectedCrops={selectedCrops} selectedRegions={selectedRegions} />,
    },
  ];

  return (
    <div>
      <CropCalendarFilters {...filterProps} />
      <Tabs tabs={calendarTabs} />
    </div>
  );
}
