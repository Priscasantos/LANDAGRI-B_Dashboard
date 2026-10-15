/* eslint-disable react-refresh/only-export-components */
import { lazy, type ComponentType, type LazyExoticComponent } from 'react';
import type { TKey } from '../i18n/types';

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
   * Fase 1 i18n: chaves do namespace `nav` resolvidas em `App.tsx` via
   * `useT('nav')`. `title`/`description` seguem como fallback PT estático
   * (mantém os testes de metadata + e2e legados verdes).
   */
  titleKey: TKey<'nav'>;
  /** @see titleKey */
  descriptionKey: TKey<'nav'>;
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
    titleKey: 'overview',
    descriptionKey: 'routeDescOverview',
  },
  {
    path: '/overview',
    Component: OverviewPage,
    title: 'Visão Geral',
    description:
      'Resumo geral e métricas-chave das iniciativas de Uso e Cobertura da Terra (LULC).',
    titleKey: 'overview',
    descriptionKey: 'routeDescOverview',
  },
  {
    path: '/initiative-analysis/*',
    Component: InitiativeAnalysisPage,
    title: 'Análise de Iniciativas',
    description:
      'Análise espaço-temporal das iniciativas de Uso e Cobertura da Terra (LULC).',
    titleKey: 'initiativeAnalysis',
    descriptionKey: 'routeDescInitiative',
  },
  {
    path: '/agricultural-analysis/*',
    Component: AgriculturalAnalysisPage,
    title: 'Análise Agrícola',
    description:
      'Indicadores agrícolas, calendário de culturas e disponibilidade agregada por região e período.',
    titleKey: 'agriculturalAnalysis',
    descriptionKey: 'routeDescAgricultural',
  },
  {
    path: '/predictive',
    Component: PredictivePage,
    title: 'Simulador Preditivo',
    description:
      'Projeções de uso da terra sob cenários de reflorestamento, expansão agrícola e adoção sustentável.',
    titleKey: 'predictive',
    descriptionKey: 'routeDescPredictive',
  },
  {
    path: '/about',
    Component: AboutPage,
    title: 'Sobre o Dashboard LANDAGRI-B',
    description:
      'Conheça os objetivos do Dashboard LANDAGRI-B e como navegar pelos seus módulos especializados.',
    titleKey: 'aboutTitle',
    descriptionKey: 'routeDescAbout',
  },
  // Catch-all: unknown paths redirect home (gh-pages SPA has no server 404).
  {
    path: '*',
    Component: OverviewPage,
    title: 'Visão Geral',
    description:
      'Resumo geral e métricas-chave das iniciativas de Uso e Cobertura da Terra (LULC).',
    titleKey: 'overview',
    descriptionKey: 'routeDescOverview',
    redirectTo: '/',
  },
];

export interface CommandIndexEntry {
  title: string;
  url: string;
  group: string;
  /**
   * Fase 1 i18n: `CommandSearch` resolve `title`/`group` via `useT('nav')`
   * no render (busca casa PT + EN + url). Campos PT mantidos para os
   * testes legados do índice.
   */
  titleKey: TKey<'nav'>;
  groupKey: TKey<'nav'>;
}

/**
 * Command-palette index: the 5 modules + initiative/agricultural sub-routes.
 * Consumed by `CommandSearch`; kept next to the route table so new
 * sub-pages are indexed in the same change that adds them.
 */
export const commandIndex: CommandIndexEntry[] = [
  { title: 'Visão Geral', url: '/overview', group: 'Visão Geral', titleKey: 'overview', groupKey: 'groupOverview' },
  {
    title: 'Análise de Iniciativas',
    url: '/initiative-analysis',
    group: 'Análise de Iniciativas',
    titleKey: 'initiativeAnalysis',
    groupKey: 'groupInitiative',
  },
  { title: 'Análise Temporal', url: '/initiative-analysis/temporal', group: 'Análise de Iniciativas', titleKey: 'temporal', groupKey: 'groupInitiative' },
  {
    title: 'Análise Comparativa',
    url: '/initiative-analysis/comparative',
    group: 'Análise de Iniciativas',
    titleKey: 'comparative',
    groupKey: 'groupInitiative',
  },
  {
    title: 'Análise Detalhada',
    url: '/initiative-analysis/detailed',
    group: 'Análise de Iniciativas',
    titleKey: 'detailed',
    groupKey: 'groupInitiative',
  },
  {
    title: 'Análise Agrícola',
    url: '/agricultural-analysis',
    group: 'Análise Agrícola',
    titleKey: 'agriculturalAnalysis',
    groupKey: 'groupAgricultural',
  },
  {
    title: 'Panorama Agrícola',
    url: '/agricultural-analysis/overview',
    group: 'Análise Agrícola',
    titleKey: 'agriOverview',
    groupKey: 'groupAgricultural',
  },
  {
    title: 'Calendário de Culturas',
    url: '/agricultural-analysis/crop-calendar',
    group: 'Análise Agrícola',
    titleKey: 'cropCalendar',
    groupKey: 'groupAgricultural',
  },
  {
    title: 'Disponibilidade Agrícola',
    url: '/agricultural-analysis/availability',
    group: 'Análise Agrícola',
    titleKey: 'availability',
    groupKey: 'groupAgricultural',
  },
  { title: 'Simulador Preditivo', url: '/predictive', group: 'Preditivo', titleKey: 'predictive', groupKey: 'groupPredictive' },
  { title: 'Sobre', url: '/about', group: 'Sobre', titleKey: 'about', groupKey: 'groupAbout' },
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
