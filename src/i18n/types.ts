/**
 * i18n fundação (Fase 1 LANDAGRI-B) — dicionário próprio leve e tipado.
 *
 * Sem react-i18next: toggle-only PT↔EN, sem rota /en. Só a UI do shell é
 * traduzida nesta fase (dados exibidos passam pelo glossário em
 * `src/data/glossary.ts`). Reversível: remover o provider volta ao PT
 * estático (dicionário `pt` é o fallback total).
 */

export type Locale = 'pt-BR' | 'en';

export const DEFAULT_LOCALE: Locale = 'pt-BR';

export const SUPPORTED_LOCALES: readonly Locale[] = ['pt-BR', 'en'];

/** Chave do localStorage (namespace `landagri-*`, como o tema). */
export const LANGUAGE_STORAGE_KEY = 'landagri-lang';

export type Namespace =
  | 'common'
  | 'nav'
  | 'overview'
  | 'initiative'
  | 'agricultural'
  | 'predictive'
  | 'about'
  | 'charts'
  | 'tables'
  | 'map'
  | 'customizer'
  | 'errors';

/** Dicionário: PT é a fonte da verdade; EN deve cobrir as mesmas chaves. */
export type Dictionary = Record<Namespace, Record<string, string>>;

export type TranslationVars = Record<string, string | number>;

import type { pt } from './dictionaries/pt';

/** Chaves tipadas por namespace, derivadas do dicionário PT. */
export type TKey<N extends Namespace> = keyof (typeof pt)[N] & string;

export function isLocale(value: unknown): value is Locale {
  return value === 'pt-BR' || value === 'en';
}

/**
 * Detecção: localStorage > navigator.language > fallback pt-BR.
 * `navigator` com prefixo `pt` resolve para pt-BR; `en` para en.
 */
export function detectLocale(
  storage: Pick<Storage, 'getItem'> | undefined,
  navigatorLanguage: string | undefined,
): Locale {
  try {
    const stored = storage?.getItem(LANGUAGE_STORAGE_KEY);
    if (isLocale(stored)) return stored;
  } catch {
    /* storage indisponível — segue para navigator */
  }
  const lang = (navigatorLanguage ?? '').toLowerCase();
  if (lang.startsWith('pt')) return 'pt-BR';
  if (lang.startsWith('en')) return 'en';
  return DEFAULT_LOCALE;
}

/** Aplica o locale ao `<html lang>` (espelha o toggle). */
export function applyDocumentLocale(locale: Locale): void {
  if (typeof document !== 'undefined') {
    document.documentElement.lang = locale;
  }
}
