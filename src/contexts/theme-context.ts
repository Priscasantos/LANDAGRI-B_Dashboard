import * as React from 'react';

export type Theme = 'light' | 'dark' | 'system';

export interface ThemeProviderState {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

/**
 * Default `undefined` para que `useTheme()` fora do provider lance erro
 * (mesmo contrato do provider anterior). Adaptado da referência
 * (`contexts/theme-context.ts`), que usa estado inicial não-nulo.
 */
export const ThemeProviderContext = React.createContext<
  ThemeProviderState | undefined
>(undefined);
