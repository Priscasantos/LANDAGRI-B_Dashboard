import { useEffect } from 'react';
import { NavLink, Link } from 'react-router-dom';
import {
  BarChart3,
  Calendar,
  Map,
  BrainCircuit,
  BookOpen,
  Sprout,
  X,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { useSidebar } from '../ui/sidebar';

interface SidebarSubItem {
  title: string;
  url: string;
}

interface SidebarNavItem {
  title: string;
  url: string;
  icon: LucideIcon;
  items?: SidebarSubItem[];
}

interface SidebarNavGroup {
  label: string;
  items: SidebarNavItem[];
}

/**
 * LANDAGRI-B section map (adapted from the shadcn-dashboard reference
 * `app-sidebar.tsx`). Demo groups (mail/tasks/chat/calendar/users/faqs/
 * pricing, auth pages, errors, settings) are intentionally dropped —
 * only the 5 product modules remain. Labels mirror `Header.tsx` so the
 * existing e2e nav assertions keep matching.
 */
const navGroups: SidebarNavGroup[] = [
  {
    label: 'Visão Geral',
    items: [
      { title: 'Visão Geral', url: '/overview', icon: BarChart3 },
    ],
  },
  {
    label: 'Análise de Iniciativas',
    items: [
      {
        title: 'Análise de Iniciativas',
        url: '/initiative-analysis',
        icon: Calendar,
        items: [
          { title: 'Análise Temporal', url: '/initiative-analysis/temporal' },
          { title: 'Análise Comparativa', url: '/initiative-analysis/comparative' },
          { title: 'Análise Detalhada', url: '/initiative-analysis/detailed' },
        ],
      },
    ],
  },
  {
    label: 'Análise Agrícola',
    items: [
      {
        title: 'Análise Agrícola',
        url: '/agricultural-analysis',
        icon: Map,
        items: [
          { title: 'Panorama Agrícola', url: '/agricultural-analysis/overview' },
          { title: 'Calendário de Culturas', url: '/agricultural-analysis/crop-calendar' },
          { title: 'Disponibilidade Agrícola', url: '/agricultural-analysis/availability' },
        ],
      },
    ],
  },
  {
    label: 'Preditivo',
    items: [
      { title: 'Simulador Preditivo', url: '/predictive', icon: BrainCircuit },
    ],
  },
  {
    label: 'Sobre',
    items: [
      { title: 'Referências', url: '/about', icon: BookOpen },
    ],
  },
];

function SidebarNavContent({ onNavigate }: { onNavigate: () => void }): React.JSX.Element {
  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-2.5 px-4 pt-5 pb-4">
        <Link
          to="/overview"
          onClick={onNavigate}
          className="flex items-center gap-2.5 rounded-lg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
          aria-label="LANDAGRI-B — ir para Visão Geral"
        >
          <span className="flex size-9 items-center justify-center rounded-lg bg-primary text-white">
            <Sprout size={20} aria-hidden="true" />
          </span>
          <span className="grid text-left leading-tight">
            <span className="truncate text-sm font-semibold text-fg">LANDAGRI-B</span>
            <span className="truncate text-xs text-fg-secondary">Agro Dashboard</span>
          </span>
        </Link>
      </div>
      <nav aria-label="Módulos do dashboard" className="flex-1 overflow-y-auto px-3 pb-4">
        {navGroups.map((group) => (
          <div key={group.label} className="mt-2 first:mt-0">
            <p className="px-3 pt-5 pb-1.5 text-[11px] font-semibold tracking-wider text-fg-muted uppercase first:pt-1">
              {group.label}
            </p>
            <ul className="space-y-1">
              {group.items.map((item) => (
                <li key={item.title}>
                  <NavLink
                    to={item.url}
                    end={item.items === undefined}
                    onClick={onNavigate}
                    className={({ isActive }: { isActive: boolean }) =>
                      `relative flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary ${
                        isActive
                          ? 'bg-sidebar-active-bg font-semibold text-sidebar-text-active before:absolute before:inset-y-1.5 before:left-0 before:w-1 before:rounded-full before:bg-primary'
                          : 'text-sidebar-text hover:bg-sidebar-hover-bg hover:text-fg'
                      }`
                    }
                  >
                    <item.icon size={17} aria-hidden="true" className="shrink-0" />
                    <span className="truncate">{item.title}</span>
                  </NavLink>
                  {item.items && (
                    <ul aria-label={`Subpáginas de ${item.title}`} className="mt-1 mb-1 ml-9 space-y-1 border-l-2 border-border pl-3">
                      {item.items.map((sub) => (
                        <li key={sub.url}>
                          <NavLink
                            to={sub.url}
                            onClick={onNavigate}
                            className={({ isActive }: { isActive: boolean }) =>
                              `block truncate rounded-md px-2.5 py-2 text-[13px] transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary ${
                                isActive
                                  ? 'bg-sidebar-active-bg font-semibold text-sidebar-text-active'
                                  : 'text-fg-secondary hover:bg-sidebar-hover-bg hover:text-fg'
                              }`
                            }
                          >
                            {sub.title}
                          </NavLink>
                        </li>
                      ))}
                    </ul>
                  )}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>
      <div className="border-t border-border px-4 py-3">
        <p className="text-[11px] text-fg-muted">LANDAGRI-B v2.4 · MapBiomas & IBGE</p>
      </div>
    </div>
  );
}

/**
 * SaaS sidebar (adapted from the reference `AppSidebar`).
 * Static rail on desktop (`lg+`), offcanvas drawer on mobile.
 * Auth (`NavUser`) is intentionally omitted in Fase 1 — no real auth yet.
 */
export default function AppSidebar(): React.JSX.Element {
  const { mobileOpen, setMobileOpen } = useSidebar();
  const close = (): void => setMobileOpen(false);
  // Escape fecha o drawer móvel e devolve o foco ao botão de menu (p3-hardening).
  // Inclui trava de scroll do body + foco inicial no botão fechar.
  useEffect(() => {
    if (!mobileOpen) return;
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    const closeBtn = document.querySelector<HTMLButtonElement>(
      '[data-testid="app-sidebar-mobile"] button[aria-label="Fechar menu de navegação"]',
    );
    closeBtn?.focus();
    const onKey = (e: KeyboardEvent): void => { if (e.key === 'Escape') { setMobileOpen(false); requestAnimationFrame(() => document.querySelector<HTMLButtonElement>('button[aria-label="Abrir menu de navegação"]')?.focus()); } };
    document.addEventListener('keydown', onKey);
    return () => {
      document.body.style.overflow = prevOverflow;
      document.removeEventListener('keydown', onKey);
    };
  }, [mobileOpen, setMobileOpen]);

  return (
    <>
      {/* Desktop rail */}
      <aside
        data-testid="app-sidebar"
        aria-label="Navegação principal"
        className="sticky top-0 hidden h-screen w-[var(--sidebar-width,260px)] shrink-0 flex-col border-r border-border bg-sidebar-bg lg:flex"
      >
        <SidebarNavContent onNavigate={() => undefined} />
      </aside>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="absolute inset-0 bg-overlay"
            onClick={close}
            aria-hidden="true"
          />
          <aside
            data-testid="app-sidebar-mobile"
            // Root cause: e2e p3-hardening espera dialog 'Menu de navegação' (substring); rótulo anterior não continha o termo.
            aria-label="Menu de navegação"
            role="dialog"
            aria-modal="true"
            className="absolute inset-y-0 left-0 flex w-[var(--sidebar-width,260px)] max-w-[85vw] flex-col border-r border-border bg-sidebar-bg shadow-lg"
          >
            <button
              type="button"
              onClick={close}
              aria-label="Fechar menu de navegação"
              className="absolute top-4 right-3 flex size-8 items-center justify-center rounded-lg text-fg-secondary transition-colors hover:bg-surface-hover hover:text-fg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
            >
              <X size={18} aria-hidden="true" />
            </button>
            <SidebarNavContent onNavigate={close} />
          </aside>
        </div>
      )}
    </>
  );
}
