/* eslint-disable react-refresh/only-export-components */
import * as React from 'react';
import {
  SidebarConfigContext,
  type SidebarConfig,
} from './sidebar-config';

interface SidebarConfigProviderProps {
  children: React.ReactNode;
}

/**
 * Adapted from the shadcn-dashboard reference (`sidebar-context.tsx`).
 * Holds collapsible-sidebar layout preferences (variant / collapsible / side).
 * Pure React — no extra dependencies. Defaults mirror the current
 * LANDAGRI-B drawer behaviour (left offcanvas-style drawer on mobile).
 */
export function SidebarConfigProvider({
  children,
}: SidebarConfigProviderProps): React.JSX.Element {
  const [config, setConfig] = React.useState<SidebarConfig>({
    variant: 'sidebar',
    collapsible: 'offcanvas',
    side: 'left',
  });

  const updateConfig = React.useCallback(
    (newConfig: Partial<SidebarConfig>) => {
      setConfig((prev) => ({ ...prev, ...newConfig }));
    },
    [],
  );

  const value = React.useMemo(
    () => ({ config, updateConfig }),
    [config, updateConfig],
  );

  return (
    <SidebarConfigContext.Provider value={value}>
      {children}
    </SidebarConfigContext.Provider>
  );
}

export function useSidebarConfig(): {
  config: SidebarConfig;
  updateConfig: (config: Partial<SidebarConfig>) => void;
} {
  const ctx = React.useContext(SidebarConfigContext);
  if (!ctx)
    throw new Error(
      'useSidebarConfig must be used within SidebarConfigProvider',
    );
  return ctx;
}
