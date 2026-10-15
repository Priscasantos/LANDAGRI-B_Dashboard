import type { ReactNode } from 'react';
import AppSidebar from './AppSidebar';
import SiteHeader from './SiteHeader';
import { SidebarProvider } from '../ui/sidebar';
import { useT } from '../../i18n/LanguageContext';

interface BaseLayoutProps {
  children: ReactNode;
  /** Module title (from the route table — replaces ModuleHeader). */
  title?: string;
  /** Module subtitle shown under the title. */
  description?: string;
}

/**
 * SaaS app shell (adapted from the reference `base-layout.tsx`).
 * Sidebar + top bar + per-module title + content + footer.
 * Skip-link e rodapé traduzidos (Fase 1 i18n, namespace `common`).
 */
export default function BaseLayout({ children, title, description }: BaseLayoutProps): React.JSX.Element {
  const { t } = useT('common');
  return (
    <SidebarProvider>
      <div className="min-h-screen bg-background lg:flex lg:items-start">
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-[70] focus:rounded-lg focus:bg-primary focus:px-3 focus:py-2 focus:text-sm focus:text-white"
        >
          {t('skipLink')}
        </a>
        <AppSidebar />
        <div className="flex min-h-screen min-w-0 flex-1 flex-col overflow-x-clip">
          <SiteHeader />
          <main
            id="main-content"
            tabIndex={-1}
            className="mx-auto w-full max-w-(--content-max-width) flex-1 px-4 py-4 sm:px-5 sm:py-5 md:py-5 lg:px-5"
          >
            {title && (
              <div className="mb-6">
                <h1 className="text-2xl font-bold tracking-tight text-foreground md:text-3xl">
                  {title}
                </h1>
                {description && (
                  <p className="mt-1.5 max-w-3xl text-sm text-muted-foreground md:text-base">
                    {description}
                  </p>
                )}
              </div>
            )}
            {children}
          </main>
          <footer className="border-t border-border bg-muted py-6 text-center text-xs text-muted-foreground">
            <div className="mx-auto w-full max-w-(--content-max-width) px-4 sm:px-6 lg:px-8">
              <p>{t('footer', { year: new Date().getFullYear() })}</p>
            </div>
          </footer>
        </div>
      </div>
    </SidebarProvider>
  );
}
