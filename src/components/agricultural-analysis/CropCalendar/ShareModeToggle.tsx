import type { ReactElement } from 'react';
import { useT } from '../../../i18n/LanguageContext';
import type { ShareMode } from '../../../lib/calendarShare';

interface ShareModeToggleProps {
  /** Modo efetivo (default área quando há `areaSharePct`, senão UFs). */
  mode: ShareMode;
  /** `false` → opção área desabilitada com nota de fallback. */
  hasArea: boolean;
  onChange: (mode: ShareMode) => void;
}

/**
 * Toggle explícito % UFs vs % área (Gaia). Sem área por UF, a opção de
 * área fica desabilitada com nota — o UI nunca sugere ponderação inexistente.
 */
export default function ShareModeToggle({ mode, hasArea, onChange }: ShareModeToggleProps): ReactElement {
  const { t } = useT('agricultural');

  const option = (value: ShareMode, disabled: boolean): ReactElement => {
    const active = mode === value;
    return (
      <button
        key={value}
        type="button"
        role="radio"
        aria-checked={active}
        aria-disabled={disabled}
        disabled={disabled}
        onClick={() => {
          if (!disabled) onChange(value);
        }}
        className={
          active
            ? 'rounded-full bg-brand px-3 py-1 text-xs font-semibold text-white shadow-sm'
            : 'rounded-full px-3 py-1 text-xs font-medium text-fg-secondary hover:text-fg disabled:cursor-not-allowed disabled:opacity-50'
        }
      >
        {value === 'uf' ? t('shareModeUf') : t('shareModeArea')}
      </button>
    );
  };

  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-xs font-medium text-fg-secondary">{t('shareModeLabel')}:</span>
      <div role="radiogroup" aria-label={t('shareModeLabel')} className="flex items-center gap-1 rounded-full bg-surface-alt p-1">
        {option('uf', false)}
        {option('area', !hasArea)}
      </div>
      {!hasArea && (
        <span className="text-xs text-fg-muted" role="note">
          {t('shareModeAreaUnavailable')}
        </span>
      )}
    </div>
  );
}
