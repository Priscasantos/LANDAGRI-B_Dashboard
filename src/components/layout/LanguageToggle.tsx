import { Languages } from 'lucide-react';
import { useLanguage, useT } from '../../i18n/LanguageContext';

/**
 * Toggle de idioma PT↔EN (Fase 1 i18n — toggle-only, sem rota /en).
 * Persiste em `landagri-lang` e atualiza o `<html lang>` via provider.
 */
export default function LanguageToggle(): React.JSX.Element {
  const { locale, toggleLocale } = useLanguage();
  const { t } = useT('common');
  const label = locale === 'pt-BR' ? t('switchToEnglish') : t('switchToPortuguese');

  return (
    <button
      type="button"
      data-testid="language-toggle"
      onClick={toggleLocale}
      aria-label={label}
      title={`${t('language')}: ${label}`}
      className="flex h-[34px] min-w-[34px] items-center justify-center gap-1 rounded-full
        bg-transparent px-1.5 text-xs font-semibold text-fg-secondary
        transition-all duration-200 hover:bg-primary hover:text-primary-foreground
        focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
    >
      <Languages size={16} aria-hidden="true" />
      <span aria-hidden="true">{locale === 'pt-BR' ? 'EN' : 'PT'}</span>
    </button>
  );
}
