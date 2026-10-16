import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Menu } from 'lucide-react';
import { useSidebar } from '../ui/sidebar';
import Breadcrumb from '../ui/breadcrumb';
import type { BreadcrumbSegment } from '../ui/breadcrumb';
import ThemeToggle from '../ui/ThemeToggle';
import ThemeCustomizer from '../ThemeCustomizer';
import LanguageToggle from './LanguageToggle';
import { CommandSearch, SearchTrigger } from './CommandSearch';
import { useT } from '../../i18n/LanguageContext';
import type { TKey } from '../../i18n/types';

const SUB_ROUTE_KEYS: Record<string, TKey<'nav'>> = {
  temporal: 'temporal',
  comparative: 'comparative',
  detailed: 'detailed',
  overview: 'agriOverview',
  'crop-calendar': 'cropCalendar',
  availability: 'availability',
};

const SECTION_KEYS: Record<string, { labelKey: TKey<'nav'>; to: string }> = {
  overview: { labelKey: 'overview', to: '/overview' },
  'initiative-analysis': { labelKey: 'initiativeAnalysis', to: '/initiative-analysis' },
  'agricultural-analysis': { labelKey: 'agriculturalAnalysis', to: '/agricultural-analysis' },
  predictive: { labelKey: 'predictive', to: '/predictive' },
  about: { labelKey: 'about', to: '/about' },
};

function useSegmentsForPath(pathname: string): BreadcrumbSegment[] {
  const { t } = useT('nav');
  const parts = pathname.split('/').filter(Boolean);
  if (parts.length === 0) return [{ label: t('overview'), to: '/overview' }];
  const [section, sub] = parts;
  const entry = SECTION_KEYS[section];
  if (!entry) return [{ label: t('overview'), to: '/overview' }];
  if (sub && SUB_ROUTE_KEYS[sub]) {
    return [
      { label: t(entry.labelKey), to: entry.to },
      { label: t(SUB_ROUTE_KEYS[sub]) },
    ];
  }
  return [{ label: t(entry.labelKey) }];
}

/**
 * Top bar of the SaaS shell (adapted from the reference `site-header.tsx`).
 * Sidebar toggle + breadcrumb + command-palette trigger + language toggle
 * (Fase 1 i18n) + theme toggle. Reference-only links dropped.
 */
export default function SiteHeader(): React.JSX.Element {
  const { toggleMobile } = useSidebar();
  const location = useLocation();
  const [searchOpen, setSearchOpen] = useState<boolean>(false);
  const { t } = useT('nav');
  const segments = useSegmentsForPath(location.pathname);

  useEffect(() => {
    const down = (event: KeyboardEvent): void => {
      if (event.key.toLowerCase() === 'k' && (event.metaKey || event.ctrlKey)) {
        event.preventDefault();
        setSearchOpen((prev) => !prev);
      }
    };
    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);

  return (
    <>
      <header className="sticky top-0 z-40 flex h-14 shrink-0 items-center gap-2 border-b border-border bg-card/95 backdrop-blur">
        <div className="flex w-full items-center gap-1.5 px-3 sm:px-4 lg:gap-2 lg:px-6">
          <button
            type="button"
            onClick={toggleMobile}
            aria-label={t('openMenu')}
            className="flex size-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary lg:hidden"
          >
            <Menu size={19} aria-hidden="true" />
          </button>
          <div className="min-w-0 flex-1">
            <Breadcrumb segments={segments} />
          </div>
          <div className="flex items-center gap-2">
            <SearchTrigger onClick={() => setSearchOpen(true)} />
            <LanguageToggle />
            <ThemeToggle />
            <ThemeCustomizer />
          </div>
        </div>
      </header>
      {searchOpen && <CommandSearch open={searchOpen} onOpenChange={setSearchOpen} />}
    </>
  );
}
