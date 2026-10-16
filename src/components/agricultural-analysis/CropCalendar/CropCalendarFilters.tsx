import { Wheat, MapPin } from 'lucide-react';
import { useT } from '../../../i18n/LanguageContext';
import { translateCropName, translateRegion } from '../../../data/glossary';

interface CropCalendarFiltersProps {
  crops: string[];
  regions: string[];
  selectedCrops: string[];
  selectedRegions: string[];
  onCropsChange: (crops: string[]) => void;
  onRegionsChange: (regions: string[]) => void;
}

export default function CropCalendarFilters({
  crops, regions, selectedCrops, selectedRegions,
  onCropsChange, onRegionsChange,
}: CropCalendarFiltersProps) {
  const { t, locale } = useT('agricultural');
  const allCropsSelected = selectedCrops.length === crops.length;
  const allRegionsSelected = selectedRegions.length === regions.length;

  const toggleCrop = (crop: string) => {
    if (selectedCrops.includes(crop)) {
      const next = selectedCrops.filter(c => c !== crop);
      onCropsChange(next.length === 0 ? crops : next);
    } else {
      onCropsChange([...selectedCrops, crop]);
    }
  };

  const toggleRegion = (region: string) => {
    if (selectedRegions.includes(region)) {
      const next = selectedRegions.filter(r => r !== region);
      onRegionsChange(next.length === 0 ? regions : next);
    } else {
      onRegionsChange([...selectedRegions, region]);
    }
  };

  const toggleAllCrops = () => {
    onCropsChange(allCropsSelected ? [] : crops);
  };

  const toggleAllRegions = () => {
    onRegionsChange(allRegionsSelected ? [] : regions);
  };

  return (
    <div className="bg-surface rounded-xl border border-border/60 shadow-sm p-4 mb-6">
      <div className="flex flex-col sm:flex-row gap-6">
        {/* Crop Filter */}
        <div className="flex-1">
          <div className="flex items-center justify-between mb-2">
            <span className="inline-flex items-center gap-1.5 text-sm font-semibold text-fg"><Wheat size={15} aria-hidden="true" className="shrink-0" /> {t('crops')}</span>
            <button
              type="button"
              onClick={toggleAllCrops}
              className="inline-flex min-h-[32px] items-center rounded-md px-2 text-xs font-medium text-amber-700 transition-colors hover:text-amber-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
            >
              {allCropsSelected ? t('deselectAll') : t('selectAll')}
            </button>
          </div>
          <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto">
            {crops.map(crop => (
              <button
                key={crop}
                type="button"
                onClick={() => toggleCrop(crop)}
                aria-pressed={selectedCrops.includes(crop)}
                className={`inline-flex min-h-[32px] items-center rounded-full border px-3 py-1 text-xs transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary ${
                  selectedCrops.includes(crop)
                    ? 'border-amber-300 bg-amber-100 font-medium text-amber-800'
                    : 'border-border bg-surface text-fg-secondary hover:border-border hover:text-fg'
                }`}
              >
                {translateCropName(crop, locale)}
              </button>
            ))}
          </div>
        </div>

        {/* Region Filter */}
        <div className="flex-1">
          <div className="flex items-center justify-between mb-2">
            <span className="inline-flex items-center gap-1.5 text-sm font-semibold text-fg"><MapPin size={15} aria-hidden="true" className="shrink-0" /> {t('regions')}</span>
            <button
              type="button"
              onClick={toggleAllRegions}
              className="inline-flex min-h-[32px] items-center rounded-md px-2 text-xs font-medium text-amber-700 transition-colors hover:text-amber-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
            >
              {allRegionsSelected ? t('deselectAll') : t('selectAll')}
            </button>
          </div>
          <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto">
            {regions.map(region => (
              <button
                key={region}
                type="button"
                onClick={() => toggleRegion(region)}
                aria-pressed={selectedRegions.includes(region)}
                className={`inline-flex min-h-[32px] items-center rounded-full border px-3 py-1 text-xs transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary ${
                  selectedRegions.includes(region)
                    ? 'border-amber-300 bg-amber-100 font-medium text-amber-800'
                    : 'border-border bg-surface text-fg-secondary hover:border-border hover:text-fg'
                }`}
              >
                {translateRegion(region, locale)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Active filters summary */}
      <div className="mt-3 pt-3 border-t border-border">
        <p className="text-xs text-fg-muted">
          {t('showing', { crops: selectedCrops.length, regions: selectedRegions.length, cropUnit: selectedCrops.length === 1 ? t('cropSingular') : t('cropPlural'), regionUnit: selectedRegions.length === 1 ? t('regionSingular') : t('regionPlural') })}
        </p>
      </div>
    </div>
  );
}
