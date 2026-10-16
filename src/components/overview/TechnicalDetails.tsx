import type { InitiativeRow } from '../../types/initiative';
import Expandable from '../ui/Expandable';
import { Building2, Microscope, History } from 'lucide-react';
import { parseAvailableYears } from '../../lib/dataParser';
import { translateMethodology, translateTerm } from '../../data/glossary';
import { useT } from '../../i18n/LanguageContext';

interface TechnicalDetailsProps {
  data: InitiativeRow;
}

export default function TechnicalDetails({ data }: TechnicalDetailsProps) {
  const { t, locale } = useT('overview');
  const years = parseAvailableYears(data.Available_Years);

  return (
    <div className="space-y-3">
      <Expandable title={t('expBasic')} icon={<Building2 size={16} aria-hidden="true" />} defaultExpanded={true}>
        <div className="space-y-2">
          <div><span className="font-medium text-fg">{t('fProvider')}</span> <span title={data.Provider || undefined}>{data.Provider || '-'}</span></div>
          <div><span className="font-medium text-fg">{t('fSource')}</span> <span title={data.Source || undefined}>{data.Source || '-'}</span></div>
          <div><span className="font-medium text-fg">{t('fCoverage')}</span> {translateTerm('coverage', data.Coverage, locale) || '-'}</div>
        </div>
      </Expandable>

      <Expandable title={t('expTech')} icon={<Microscope size={16} aria-hidden="true" />}>
        <div className="space-y-2">
          <div><span className="font-medium text-fg">{t('fMethodology')}</span> {translateMethodology(data.Methodology, locale) || '-'}</div>
          <div><span className="font-medium text-fg">{t('fAlgorithm')}</span> <span title={data.Algorithm || undefined}>{translateMethodology(data.Algorithm, locale) || '-'}</span></div>
          <div><span className="font-medium text-fg">{t('fResolution')}</span> {data.Resolution > 0 ? `${data.Resolution}m` : '-'}</div>
          <div><span className="font-medium text-fg">{t('fReference')}</span> {data.Reference_System || '-'}</div>
        </div>
      </Expandable>

      <Expandable title={t('expTemporal')} icon={<History size={16} aria-hidden="true" />}>
        <div className="space-y-2">
          {years.length > 0 ? (
            <>
              <div><span className="font-medium text-fg">{t('fFirstYear')}</span> {Math.min(...years)}</div>
              <div><span className="font-medium text-fg">{t('fLastYear')}</span> {Math.max(...years)}</div>
              <div><span className="font-medium text-fg">{t('fTotalYears')}</span> {years.length}</div>
            </>
          ) : (
            <div className="text-fg-muted italic">{t('noTemporal')}</div>
          )}
        </div>
      </Expandable>
    </div>
  );
}
