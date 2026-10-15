import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Menu } from 'lucide-react';
import { useSidebar } from '../ui/sidebar';
import Breadcrumb from '../ui/breadcrumb';
import type { BreadcrumbSegment } from '../ui/breadcrumb';
import ThemeToggle from '../ui/ThemeToggle';
import ThemeCustomizer from '../ThemeCustomizer';
import { CommandSearch, SearchTrigger } from './CommandSearch';

const SUB_ROUTE_LABELS: Record<string, string> = {
  temporal: 'Análise Temporal',
  comparative: 'Análise Comparativa',
  detailed: 'Análise Detalhada',
  overview: 'Panorama Agrícola',
  'crop-calendar': 'Calendário de Culturas',
  availability: 'Disponibilidade Agrícola',
};

const SECTION_LABELS: Record<string, { label: string; to: string }> = {
  overview: { label: 'Visão Geral', to: '/overview' },
  'initiative-analysis': { label: 'Análise de Iniciativas', to: '/initiative-analysis' },
  'agricultural-analysis': { label: 'Análise Agrícola', to: '/agricultural-analysis' },
  predictive: { label: 'Simulador Preditivo', to: '/predictive' },
  about: { label: 'Referências', to: '/about' },
};

function segmentsForPath(pathname: string): BreadcrumbSegment[] {
  const parts = pathname.split('/').filter(Boolean);
  if (parts.length === 0) return [{ label: 'Visão Geral', to: '/overview' }];
  const [section, sub] = parts;
  const entry = SECTION_LABELS[section];
  if (!entry) return [{ label: 'Visão Geral', to: '/overview' }];
  if (sub && SUB_ROUTE_LABELS[sub]) {
    return [
      { label: entry.label, to: entry.to },
      { label: SUB_ROUTE_LABELS[sub] },
    ];
  }
  return [{ label: entry.label }];
}

/**
 * Top bar of the SaaS shell (adapted from the reference `site-header.tsx`).
 * Sidebar toggle + breadcrumb + command-palette trigger + theme toggle.
 * Reference-only links (Blocks / Landing / GitHub) are dropped.
 */
export default function SiteHeader(): React.JSX.Element {
  const { toggleMobile } = useSidebar();
  const location = useLocation();
  const [searchOpen, setSearchOpen] = useState<boolean>(false);

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
            aria-label="Abrir menu de navegação"
            className="flex size-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary lg:hidden"
          >
            <Menu size={19} aria-hidden="true" />
          </button>
          <div className="min-w-0 flex-1">
            <Breadcrumb segments={segmentsForPath(location.pathname)} />
          </div>
          <div className="flex items-center gap-2">
            <SearchTrigger onClick={() => setSearchOpen(true)} />
            <ThemeToggle />
            <ThemeCustomizer />
          </div>
        </div>
      </header>
      {searchOpen && <CommandSearch open={searchOpen} onOpenChange={setSearchOpen} />}
    </>
  );
}
