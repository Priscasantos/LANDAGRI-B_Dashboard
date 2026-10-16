import type { ReactElement } from 'react';
import { useT } from '../../../i18n/LanguageContext';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { phenoPhaseColor } from '../../../lib/phenoColors';

/**
 * Legenda fenológica fixa cross-tab (Gaia): Plantio / Colheita / PH com
 * hachura + nota de codificação (cor = fase; cultura/região = rótulo).
 */
export default function PhenologyLegend(): ReactElement {
  const { t } = useT('agricultural');
  const theme = useEffectiveTheme();
  const planting = phenoPhaseColor('P', theme);
  const harvest = phenoPhaseColor('H', theme);

  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-1" role="note" aria-label={t('matrixLegend')}>
      <span className="inline-flex items-center gap-1.5 text-xs text-fg-secondary">
        <span
          aria-hidden="true"
          className="inline-block h-3 w-5 rounded-sm border"
          style={{ backgroundColor: planting, borderColor: planting }}
        />
        {t('tipPlanting')}
      </span>
      <span className="inline-flex items-center gap-1.5 text-xs text-fg-secondary">
        <span
          aria-hidden="true"
          className="inline-block h-3 w-5 rounded-sm border"
          style={{ backgroundColor: harvest, borderColor: harvest }}
        />
        {t('tipHarvest')}
      </span>
      <span className="inline-flex items-center gap-1.5 text-xs text-fg-secondary" title={t('legendBothNote')}>
        <span
          aria-hidden="true"
          className="inline-block h-3 w-5 rounded-sm border"
          style={{
            backgroundColor: planting,
            backgroundImage: `repeating-linear-gradient(45deg, transparent 0 2px, ${harvest} 2px 4px)`,
            borderColor: planting,
          }}
        />
        {t('legendBoth')}
      </span>
      <span className="text-xs text-fg-muted">{t('legendCodingNote')}</span>
    </div>
  );
}
