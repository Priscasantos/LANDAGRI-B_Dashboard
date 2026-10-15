/* eslint-disable react-refresh/only-export-components */
import { lazy, type ComponentType, type LazyExoticComponent } from 'react';

/**
 * Basename default (gh-pages). Override with `VITE_BASENAME` env.
 * `VITE_BASENAME` is the single source of truth — `vite.config.ts`
 * derives `base` from the same variable, and `index.html` uses
 * `%BASE_URL%` so no path is hardcoded twice.
 *
 * Rule (must match `vite.config.ts`):
 * - explicit `VITE_BASENAME` (non-empty) always wins;
 * - otherwise `/` in dev (`vite dev` serves at root);
 * - otherwise the gh-pages default in prod builds.
 *
 * Accepts an optional env override so unit tests stay deterministic
 * without stubbing Vite's boolean `DEV`/`PROD` flags.
 */
export const DEFAULT_BASENAME = '/LANDAGRI-B_Dashboard';

interface BasenameEnv {
  VITE_BASENAME?: string;
  DEV?: boolean;
}

function normalizeBasename(raw: string): string {
  const trimmed = raw.trim();
  if (!trimmed || trimmed === '/') return '/';
  const withLeading = trimmed.startsWith('/') ? trimmed : `/${trimmed}`;
  return withLeading.replace(/\/+$/, '') || '/';
}

export function getBasename(env: BasenameEnv = import.meta.env): string {
  const raw = env.VITE_BASENAME;
  if (raw && raw.trim()) return normalizeBasename(raw);
  if (env.DEV) return '/';
  return DEFAULT_BASENAME;
}

export interface AppRoute {
  path: string;
  Component: LazyExoticComponent<ComponentType>;
  /** Header title rendered by BaseLayout (replaces ModuleHeader). */
  title: string;
  /** Header subtitle rendered by BaseLayout. */
  description: string;
  /**
   * When set, App.tsx renders `<Navigate to={redirectTo} replace />`
   * instead of the lazy Component (used by the catch-all 404 route).
   */
  redirectTo?: string;
}

const OverviewPage = lazy(() => import('../pages/OverviewPage'));
const InitiativeAnalysisPage = lazy(
  () => import('../pages/InitiativeAnalysisPage'),
);
const AgriculturalAnalysisPage = lazy(
  () => import('../pages/AgriculturalAnalysisPage'),
);
const PredictivePage = lazy(() => import('../pages/PredictivePage'));
const AboutPage = lazy(() => import('../pages/AboutPage'));

/**
 * Declarative route table — preserves the 5 existing routes.
 * Rendered by `App.tsx` inside `<Routes>` with Suspense + ErrorBoundary;
 * each route carries the title/description `BaseLayout` renders as the
 * module header (replaces per-page `ModuleHeader`).
 */
export const appRoutes: AppRoute[] = [
  {
    path: '/',
    Component: OverviewPage,
    title: 'Visão Geral',
    description:
      'Resumo geral e métricas-chave das iniciativas de Uso e Cobertura da Terra (LULC).',
  },
  {
    path: '/overview',
    Component: OverviewPage,
    title: 'Visão Geral',
    description:
      'Resumo geral e métricas-chave das iniciativas de Uso e Cobertura da Terra (LULC).',
  },
  {
    path: '/initiative-analysis/*',
    Component: InitiativeAnalysisPage,
    title: 'Análise de Iniciativas',
    description:
      'Análise espaço-temporal das iniciativas de Uso e Cobertura da Terra (LULC).',
  },
  {
    path: '/agricultural-analysis/*',
    Component: AgriculturalAnalysisPage,
    title: 'Análise Agrícola',
    description:
      'Indicadores agrícolas, calendário de culturas e disponibilidade agregada por região e período.',
  },
  {
    path: '/predictive',
    Component: PredictivePage,
    title: 'Simulador Preditivo',
    description:
      'Projeções de uso da terra sob cenários de reflorestamento, expansão agrícola e adoção sustentável.',
  },
  {
    path: '/about',
    Component: AboutPage,
    title: 'Referências',
    description:
      'Fontes de dados, metodologia e referências do dashboard LANDAGRI-B.',
  },
  // Catch-all: unknown paths redirect home (gh-pages SPA has no server 404).
  {
    path: '*',
    Component: OverviewPage,
    title: 'Visão Geral',
    description:
      'Resumo geral e métricas-chave das iniciativas de Uso e Cobertura da Terra (LULC).',
    redirectTo: '/',
  },
];

export interface CommandIndexEntry {
  title: string;
  url: string;
  group: string;
}

/**
 * Command-palette index: the 5 modules + initiative/agricultural sub-routes.
 * Consumed by `CommandSearch`; kept next to the route table so new
 * sub-pages are indexed in the same change that adds them.
 */
export const commandIndex: CommandIndexEntry[] = [
  { title: 'Visão Geral', url: '/overview', group: 'Overview' },
  {
    title: 'Análise de Iniciativas',
    url: '/initiative-analysis',
    group: 'Initiative Analysis',
  },
  { title: 'Temporal Analysis', url: '/initiative-analysis/temporal', group: 'Initiative Analysis' },
  {
    title: 'Comparative Analysis',
    url: '/initiative-analysis/comparative',
    group: 'Initiative Analysis',
  },
  {
    title: 'Detailed Analysis',
    url: '/initiative-analysis/detailed',
    group: 'Initiative Analysis',
  },
  {
    title: 'Análise Agrícola',
    url: '/agricultural-analysis',
    group: 'Agricultural Analysis',
  },
  {
    title: 'Agriculture Overview',
    url: '/agricultural-analysis/overview',
    group: 'Agricultural Analysis',
  },
  {
    title: 'Crop Calendar',
    url: '/agricultural-analysis/crop-calendar',
    group: 'Agricultural Analysis',
  },
  {
    title: 'Agriculture Availability',
    url: '/agricultural-analysis/availability',
    group: 'Agricultural Analysis',
  },
  { title: 'Simulador Preditivo', url: '/predictive', group: 'Predictive' },
  { title: 'Referências', url: '/about', group: 'About' },
];

/** Session-storage key written by `public/404.html` on gh-pages deep links. */
export const REDIRECT_STORAGE_KEY = 'redirectPath';

export interface RedirectStorage {
  getItem: (key: string) => string | null;
  removeItem: (key: string) => void;
}

/**
 * Reads + consumes the deep-link path saved by the gh-pages SPA fallback.
 * Returns the path when it is a valid in-app deep link, else `null`.
 * Extracted from `App.tsx` so the 404-restore rule is unit-testable.
 */
export function getRedirectPath(storage: RedirectStorage): string | null {
  const raw = storage.getItem(REDIRECT_STORAGE_KEY);
  if (!raw || !raw.startsWith('/') || raw === '/') return null;
  storage.removeItem(REDIRECT_STORAGE_KEY);
  return raw;
}
