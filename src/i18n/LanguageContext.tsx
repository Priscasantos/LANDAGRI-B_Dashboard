/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { getActiveLocale, translate } from './index';
import {
  DEFAULT_LOCALE,
  LANGUAGE_STORAGE_KEY,
  applyDocumentLocale,
  detectLocale,
  type Locale,
  type Namespace,
  type TKey,
  type TranslationVars,
} from './types';

interface LanguageContextValue {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  toggleLocale: () => void;
}

/**
 * Default = PT estático: componentes fora do provider (ex. testes sem
 * wrapper) continuam renderizando pt-BR em vez de quebrar.
 */
const LanguageContext = createContext<LanguageContextValue>({
  locale: DEFAULT_LOCALE,
  setLocale: () => undefined,
  toggleLocale: () => undefined,
});

function persistLocale(locale: Locale): void {
  try {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, locale);
  } catch {
    /* private mode — locale segue só em memória + <html lang> */
  }
  applyDocumentLocale(locale);
}

export function LanguageProvider({ children }: { children: ReactNode }): React.JSX.Element {
  const [locale, setLocaleState] = useState<Locale>(() => {
    const detected =
      typeof window === 'undefined'
        ? DEFAULT_LOCALE
        : detectLocale(localStorage, navigator.language);
    return detected;
  });

  // Sincroniza o <html lang> no mount (toggle-only, sem rota /en).
  useEffect(() => {
    applyDocumentLocale(locale);
  }, [locale]);

  const setLocale = useCallback((next: Locale) => {
    setLocaleState(next);
    persistLocale(next);
  }, []);

  const toggleLocale = useCallback(() => {
    setLocaleState((prev) => {
      const next: Locale = prev === 'pt-BR' ? 'en' : 'pt-BR';
      persistLocale(next);
      return next;
    });
  }, []);

  const value = useMemo(
    () => ({ locale, setLocale, toggleLocale }),
    [locale, setLocale, toggleLocale],
  );

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage(): LanguageContextValue {
  return useContext(LanguageContext);
}

/** Retorna o locale ativo fora do React (mesma regra do provider). */
export function useActiveLocaleSnapshot(): Locale {
  return getActiveLocale();
}

/**
 * `useT('nav')` → `{ t, locale }` com chaves tipadas do namespace.
 * Fallback pt-BR por chave (ver `translate`).
 */
export function useT<N extends Namespace>(
  namespace: N,
): {
  t: (key: TKey<N>, vars?: TranslationVars) => string;
  locale: Locale;
} {
  const { locale } = useLanguage();
  const t = useCallback(
    (key: TKey<N>, vars?: TranslationVars) => translate(locale, namespace, key, vars),
    [locale, namespace],
  );
  return { t, locale };
}
