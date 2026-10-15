import { useEffect, useRef, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BarChart3,
  Calendar,
  Map,
  BrainCircuit,
  BookOpen,
  Menu,
  X,
} from 'lucide-react';
import ThemeToggle from './ui/ThemeToggle';
import ThemeCustomizer from './ThemeCustomizer';

type TabId = 'overview' | 'initiative-analysis' | 'agricultural-analysis' | 'predictive' | 'about';

interface TabConfig {
  id: TabId;
  label: string;
  shortLabel: string;
  path: string;
  icon: React.ElementType;
}


const tabs: TabConfig[] = [
  { id: 'overview', label: 'Visão Geral', shortLabel: 'Visão Geral', path: '/overview', icon: BarChart3 },
  { id: 'initiative-analysis', label: 'Análise de Iniciativas', shortLabel: 'Iniciativas', path: '/initiative-analysis', icon: Calendar },
  { id: 'agricultural-analysis', label: 'Análise Agrícola', shortLabel: 'Agrícola', path: '/agricultural-analysis', icon: Map },
  { id: 'predictive', label: 'Simulador Preditivo', shortLabel: 'Simulador', path: '/predictive', icon: BrainCircuit },
  { id: 'about', label: 'Referências', shortLabel: 'Referências', path: '/about', icon: BookOpen },
];


export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const drawerRef = useRef<HTMLDivElement>(null);
  const menuButtonRef = useRef<HTMLButtonElement>(null);
  const prevOpenRef = useRef(false);

  const activeTab = tabs.find((t) => location.pathname.startsWith(t.path))?.id ?? 'overview';

  // NOTE: drawer links close via onClick (event handler, not an effect).
  // Browser back/forward with an open drawer is a non-issue: the drawer
  // is mobile-only transient UI and closes on Escape / overlay tap.
  // Escape to close + lightweight Tab focus-trap while the drawer is open.
  useEffect(() => {
    if (!mobileMenuOpen) return;
    const onKeyDown = (e: KeyboardEvent): void => {
      if (e.key === 'Escape') {
        setMobileMenuOpen(false);
        return;
      }
      if (e.key === 'Tab' && drawerRef.current) {
        const focusables = drawerRef.current.querySelectorAll<HTMLElement>(
          'a[href], button:not([disabled])',
        );
        if (focusables.length === 0) return;
        const first = focusables[0];
        const last = focusables[focusables.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [mobileMenuOpen]);

  // Body scroll lock while the drawer is open.
  useEffect(() => {
    if (!mobileMenuOpen) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = prev;
    };
  }, [mobileMenuOpen]);

  // Return focus to the menu button when the drawer closes (keyboard users).
  useEffect(() => {
    if (prevOpenRef.current && !mobileMenuOpen) {
      menuButtonRef.current?.focus();
    }
    prevOpenRef.current = mobileMenuOpen;
  }, [mobileMenuOpen]);

  return (
    <>
      {/* Desktop Header (md+) */}
      <header className="sticky top-0 z-40 bg-surface border-b border-border shadow-sm hidden md:block">
        <div className="flex items-center justify-between h-14 px-6">
          {/* Logo */}
          <div className="flex items-center gap-3 shrink-0">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
              style={{
                background: 'linear-gradient(135deg, var(--color-primary) 0%, #1e40af 100%)',
              }}
            >
              <BarChart3 size={16} className="text-white" />
            </div>
            <div className="flex items-baseline gap-2">
              <h1 className="text-sm font-bold tracking-tight text-fg">
                LANDAGRI-B
              </h1>
              <span className="text-[10px] font-mono text-fg-muted hidden lg:inline">
                Dashboard de Análise Territorial
              </span>
            </div>
          </div>

          {/* Desktop Tabs - centered */}
          <nav className="flex items-center gap-0.5 mx-auto px-4" aria-label="Navegação principal">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = tab.id === activeTab;
              return (
                <Link
                  key={tab.id}
                  to={tab.path}
                  aria-current={isActive ? 'page' : undefined}
                  className={`
                    relative flex items-center gap-2 px-3 py-2 text-xs font-semibold transition-all cursor-pointer rounded-lg
                    ${isActive
                      ? 'text-fg'
                      : 'text-fg-secondary hover:text-fg hover:bg-surface-hover'
                    }
                  `}
                >
                  <Icon size={15} />
                  <span className="hidden lg:inline">{tab.label}</span>
                  <span className="lg:hidden">{tab.shortLabel}</span>
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute bottom-0 left-2 right-2 h-0.5 bg-primary rounded-full"
                    />
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Right */}
          <div className="flex items-center gap-2">
            <ThemeCustomizer />
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Mobile Header (< md) */}
      <header className="sticky top-0 z-40 bg-surface border-b border-border md:hidden">
        <div className="flex items-center justify-between h-12 px-4">
          <button
            ref={menuButtonRef}
            onClick={() => setMobileMenuOpen(true)}
            className="p-2 -ml-2 rounded-lg text-fg-secondary hover:text-fg hover:bg-surface-hover active:bg-surface-hover cursor-pointer"
            aria-label="Abrir menu"
            aria-expanded={mobileMenuOpen}
            aria-controls="mobile-nav-drawer"
          >
            <Menu size={20} />
          </button>

          <div className="flex items-center gap-2">
            <div
              className="w-7 h-7 rounded-lg flex items-center justify-center"
              style={{
                background: 'linear-gradient(135deg, var(--color-primary) 0%, #1e40af 100%)',
              }}
            >
              <BarChart3 size={14} className="text-white" />
            </div>
            <span className="text-xs font-bold text-fg">
              {tabs.find(t => t.id === activeTab)?.shortLabel || 'Visão Geral'}
            </span>
          </div>

          <div className="flex items-center gap-1">
            <ThemeCustomizer />
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Mobile Slide-in Drawer */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="fixed inset-0 z-50 bg-black/40 md:hidden"
              onClick={() => setMobileMenuOpen(false)}
              aria-hidden="true"
            />

            <motion.div
              ref={drawerRef}
              id="mobile-nav-drawer"
              role="dialog"
              aria-modal="true"
              aria-label="Menu de navegação"
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 30, stiffness: 300 }}
              className="fixed top-0 left-0 bottom-0 z-50 w-72 bg-surface border-r border-border shadow-xl md:hidden"
            >
              <div className="flex items-center justify-between p-4 border-b border-border">
                <div className="flex items-center gap-2">
                  <div
                    className="w-8 h-8 rounded-lg flex items-center justify-center"
                    style={{
                      background: 'linear-gradient(135deg, var(--color-primary) 0%, #1e40af 100%)',
                    }}
                  >
                    <BarChart3 size={16} className="text-white" />
                  </div>
                  <span className="text-sm font-bold text-fg">LANDAGRI-B</span>
                </div>
                <button
                  autoFocus
                  onClick={() => setMobileMenuOpen(false)}
                  className="p-2 rounded-lg text-fg-secondary hover:text-fg hover:bg-surface-hover cursor-pointer"
                  aria-label="Fechar menu"
                >
                  <X size={18} />
                </button>
              </div>

              <nav className="p-3 space-y-1" aria-label="Menu móvel">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  const isActive = tab.id === activeTab;
                  return (
                    <Link
                      key={tab.id}
                      to={tab.path}
                      onClick={() => setMobileMenuOpen(false)}
                      aria-current={isActive ? 'page' : undefined}
                      className={`
                        flex items-center gap-3 w-full p-3 rounded-xl text-sm font-semibold cursor-pointer transition-all
                        ${isActive
                          ? 'bg-primary-light text-fg'
                          : 'text-fg-secondary hover:text-fg hover:bg-surface-hover'
                        }
                      `}
                    >
                      <Icon size={18} />
                      <span>{tab.label}</span>
                      {isActive && (
                        <span className="ml-auto w-1.5 h-1.5 rounded-full bg-primary" />
                      )}
                    </Link>
                  );
                })}
              </nav>

              <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-border">
                <p className="text-[10px] text-fg-muted text-center">
                  LANDAGRI-B v2.4
                </p>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
