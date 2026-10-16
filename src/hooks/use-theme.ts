import * as React from 'react';
import { ThemeProviderContext } from '../contexts/theme-context';

export function useTheme() {
  const context = React.useContext(ThemeProviderContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

/**
 * Resolve o tema efetivo (`light` | `dark`), expandindo `system` via
 * `prefers-color-scheme`. Re-renderiza quando o SO muda em modo `system`.
 */
export function useEffectiveTheme(): 'light' | 'dark' {
  const { theme } = useTheme();
  const [systemDark, setSystemDark] = React.useState<boolean>(() =>
    typeof window !== 'undefined' &&
    typeof window.matchMedia === 'function'
      ? window.matchMedia('(prefers-color-scheme: dark)').matches
      : false,
  );

  React.useEffect(() => {
    if (theme !== 'system') return;
    if (typeof window.matchMedia !== 'function') return;
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = (e: MediaQueryListEvent): void => setSystemDark(e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, [theme]);

  if (theme === 'dark') return 'dark';
  if (theme === 'light') return 'light';
  return systemDark ? 'dark' : 'light';
}
