import * as React from 'react';
import {
  ThemeProviderContext,
  type Theme,
  type ThemeProviderState,
} from '../contexts/theme-context';

interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: Theme;
  storageKey?: string;
}

const VALID_THEMES: readonly Theme[] = ['light', 'dark', 'system'];

function readStoredTheme(storageKey: string, fallback: Theme): Theme {
  try {
    const stored = localStorage.getItem(storageKey) as Theme | null;
    if (stored && VALID_THEMES.includes(stored)) return stored;
  } catch {
    /* private mode / SSR — usa fallback */
  }
  return fallback;
}

function resolveSystemTheme(): 'light' | 'dark' {
  if (
    typeof window !== 'undefined' &&
    typeof window.matchMedia === 'function' &&
    window.matchMedia('(prefers-color-scheme: dark)').matches
  ) {
    return 'dark';
  }
  return 'light';
}

/**
 * Theme provider with `system` support (adapted from the shadcn-dashboard
 * reference `theme-provider.tsx`).
 *
 * - Storage key `landagri-theme` (compatível com o provider anterior —
 *   valores `light`/`dark` existentes são reaproveitados).
 * - `system` resolve via `prefers-color-scheme` e acompanha mudanças do SO.
 * - Aplica `.light`/`.dark` em `document.documentElement` (Tailwind
 *   `@custom-variant dark`). Single provider — sem FOUC/duplo provider.
 */
export function ThemeProvider({
  children,
  defaultTheme = 'system',
  storageKey = 'landagri-theme',
}: ThemeProviderProps): React.JSX.Element {
  const [theme, setThemeState] = React.useState<Theme>(() =>
    readStoredTheme(storageKey, defaultTheme),
  );

  React.useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark');
    const resolved = theme === 'system' ? resolveSystemTheme() : theme;
    root.classList.add(resolved);
    // Espelha o script pré-paint do index.html (controles nativos/scrollbar).
    root.style.colorScheme = resolved;
  }, [theme]);

  // Acompanha mudanças do SO enquanto estiver em `system`.
  React.useEffect(() => {
    if (theme !== 'system') return;
    if (typeof window.matchMedia !== 'function') return;
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = (e: MediaQueryListEvent): void => {
      const root = window.document.documentElement;
      root.classList.remove('light', 'dark');
      root.classList.add(e.matches ? 'dark' : 'light');
      root.style.colorScheme = e.matches ? 'dark' : 'light';
    };
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, [theme]);

  const value = React.useMemo<ThemeProviderState>(
    () => ({
      theme,
      setTheme: (next: Theme) => {
        try {
          localStorage.setItem(storageKey, next);
        } catch {
          /* armazenamento indisponível — mantém só em memória */
        }
        setThemeState(next);
      },
    }),
    [theme, storageKey],
  );

  return (
    <ThemeProviderContext.Provider value={value}>
      {children}
    </ThemeProviderContext.Provider>
  );
}
