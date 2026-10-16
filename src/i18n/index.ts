import { pt } from './dictionaries/pt';
import { en } from './dictionaries/en';
import {
  DEFAULT_LOCALE,
  type Dictionary,
  type Locale,
  type Namespace,
  type TKey,
  type TranslationVars,
} from './types';

const dictionaries: Record<Locale, Dictionary> = { 'pt-BR': pt, en };

/** Locale ativo fora do React (Plotly `separators`, ErrorBoundary, etc.). */
export function getActiveLocale(): Locale {
  if (typeof document !== 'undefined') {
    const htmlLang = document.documentElement.lang;
    if (htmlLang.toLowerCase().startsWith('pt')) return 'pt-BR';
    if (htmlLang.toLowerCase().startsWith('en')) return 'en';
  }
  try {
    const stored = localStorage.getItem('landagri-lang');
    if (stored === 'pt-BR' || stored === 'en') return stored;
  } catch {
    /* sem storage — fallback */
  }
  return DEFAULT_LOCALE;
}

function interpolate(template: string, vars?: TranslationVars): string {
  if (!vars) return template;
  return Object.entries(vars).reduce(
    (acc, [key, value]) => acc.replace(`{${key}}`, String(value)),
    template,
  );
}

/**
 * Tradução com fallback pt-BR: `en[ns][key] ?? pt[ns][key] ?? key`.
 * Nunca retorna `undefined` — chave órfã renderiza a própria chave.
 */
export function translate<N extends Namespace>(
  locale: Locale,
  namespace: N,
  key: TKey<N>,
  vars?: TranslationVars,
): string {
  const table = dictionaries[locale]?.[namespace] as
    | Record<string, string>
    | undefined;
  const fallback = pt[namespace] as Record<string, string>;
  const template = table?.[key] ?? fallback[key] ?? key;
  return interpolate(template, vars);
}
