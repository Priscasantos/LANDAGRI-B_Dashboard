/* eslint-disable react-refresh/only-export-components */
import { createContext, useCallback, useContext, useMemo, useState } from 'react';
import type { ReactNode } from 'react';

interface SidebarContextValue {
  /** Mobile drawer open state (desktop sidebar is always visible). */
  mobileOpen: boolean;
  setMobileOpen: (open: boolean) => void;
  toggleMobile: () => void;
}

const SidebarContext = createContext<SidebarContextValue | null>(null);

interface SidebarProviderProps {
  children: ReactNode;
}

/**
 * Drawer-state provider for the SaaS shell (adapted from the
 * shadcn-dashboard reference `SidebarProvider`).
 *
 * Only owns the mobile offcanvas state. Visual variant/collapsible/side
 * preferences stay in `SidebarConfigProvider` (`src/contexts/`), which
 * keeps wrapping the app in `App.tsx`.
 */
export function SidebarProvider({ children }: SidebarProviderProps): React.JSX.Element {
  const [mobileOpen, setMobileOpen] = useState<boolean>(false);

  const toggleMobile = useCallback(() => {
    setMobileOpen((prev) => !prev);
  }, []);

  const value = useMemo(
    () => ({ mobileOpen, setMobileOpen, toggleMobile }),
    [mobileOpen, toggleMobile],
  );

  return <SidebarContext.Provider value={value}>{children}</SidebarContext.Provider>;
}

export function useSidebar(): SidebarContextValue {
  const ctx = useContext(SidebarContext);
  if (!ctx) throw new Error('useSidebar must be used within SidebarProvider');
  return ctx;
}
