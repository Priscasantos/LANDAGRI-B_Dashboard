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
              onClick={toggleAllCrops}
              className="text-xs text-amber-700 hover:text-amber-800 font-medium"
            >
              {allCropsSelected ? t('deselectAll') : t('selectAll')}
            </button>
          </div>
          <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto">
            {crops.map(crop => (
              <button
                key={crop}
                onClick={() => toggleCrop(crop)}
                className={`px-2.5 py-1 text-xs rounded-full border transition-colors ${
                  selectedCrops.includes(crop)
                    ? 'bg-amber-100 border-amber-300 text-amber-800 font-medium'
                    : 'bg-surface border-border text-fg-secondary hover:border-border'
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
              onClick={toggleAllRegions}
              className="text-xs text-amber-700 hover:text-amber-800 font-medium"
            >
              {allRegionsSelected ? t('deselectAll') : t('selectAll')}
            </button>
          </div>
          <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto">
            {regions.map(region => (
              <button
                key={region}
                onClick={() => toggleRegion(region)}
                className={`px-2.5 py-1 text-xs rounded-full border transition-colors ${
                  selectedRegions.includes(region)
                    ? 'bg-amber-100 border-amber-300 text-amber-800 font-medium'
                    : 'bg-surface border-border text-fg-secondary hover:border-border'
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
