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
    title: 'Iniciativas',
    description:
      'Análise espaço-temporal das iniciativas de Uso e Cobertura da Terra (LULC).',
    titleKey: 'initiativeAnalysis',
    descriptionKey: 'routeDescInitiative',
  },
  {
    path: '/agricultural-analysis/*',
    Component: AgriculturalAnalysisPage,
    title: 'Agricultura',
    description:
      'Indicadores agrícolas, calendário de culturas e disponibilidade agregada por região e período.',
    titleKey: 'agriculturalAnalysis',
    descriptionKey: 'routeDescAgricultural',
  },
  {
    path: '/predictive',
    Component: PredictivePage,
    title: 'Simulador',
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
  /**
   * Fase 3 IA enxuta: sinônimos PT+EN + tokens de url para a busca da
   * paleta casar ("temporal", "calendar", "simulador", …) independente
   * do locale ativo. Espaço-separado, minúsculas, sem acento duplicado
   * quando o termo canônico já cobre.
   */
  keywords: string;
}

/**
 * Command-palette index: the 5 modules + initiative/agricultural sub-routes.
 * Consumed by `CommandSearch`; kept next to the route table so new
 * sub-pages are indexed in the same change that adds them.
 *
 * Fase 3 IA enxuta: títulos curtos (~14 chars, espelham o dicionário `nav`
 * PT); `keywords` carrega os sinônimos longos PT+EN para a busca não
 * perder recall ("análise temporal", "crop calendar", …).
 */
export const commandIndex: CommandIndexEntry[] = [
  { title: 'Visão Geral', url: '/overview', group: 'Visão Geral', titleKey: 'overview', groupKey: 'groupOverview', keywords: 'overview dashboard home inicio start geral' },
  {
    title: 'Iniciativas',
    url: '/initiative-analysis',
    group: 'Território',
    titleKey: 'initiativeAnalysis',
    groupKey: 'groupInitiative',
    keywords: 'analise iniciativas initiatives territory territorio analise-de-iniciativas initiative-analysis',
  },
  { title: 'Evolução', url: '/initiative-analysis/temporal', group: 'Território', titleKey: 'temporal', groupKey: 'groupInitiative', keywords: 'temporal evolucao evolution serie series tempo time historico history analise-temporal' },
  {
    title: 'Comparar',
    url: '/initiative-analysis/comparative',
    group: 'Território',
    titleKey: 'comparative',
    groupKey: 'groupInitiative',
    keywords: 'comparar comparativo comparativa compare comparison pairwise par analise-comparativa',
  },
  {
    title: 'Ficha',
    url: '/initiative-analysis/detailed',
    group: 'Território',
    titleKey: 'detailed',
    groupKey: 'groupInitiative',
    keywords: 'ficha detalhada detalhe detail details fact-sheet tecnica analise-detalhada',
  },
  {
    title: 'Agricultura',
    url: '/agricultural-analysis',
    group: 'Agricultura',
    titleKey: 'agriculturalAnalysis',
    groupKey: 'groupAgricultural',
    keywords: 'agricultura agriculture agricola agricultural analise-agricola agricultural-analysis',
  },
  {
    title: 'Panorama',
    url: '/agricultural-analysis/overview',
    group: 'Agricultura',
    titleKey: 'agriOverview',
    groupKey: 'groupAgricultural',
    keywords: 'panorama overview snapshot geral farms panorama-agricola',
  },
  {
    title: 'Calendário',
    url: '/agricultural-analysis/crop-calendar',
    group: 'Agricultura',
    titleKey: 'cropCalendar',
    groupKey: 'groupAgricultural',
    keywords: 'calendario calendar crop culturas safras plantio colheita crop-calendar',
  },
  {
    title: 'Disponibilidade',
    url: '/agricultural-analysis/availability',
    group: 'Agricultura',
    titleKey: 'availability',
    groupKey: 'groupAgricultural',
    keywords: 'disponibilidade availability estoque supply agricola',
  },
  { title: 'Simulador', url: '/predictive', group: 'Mais', titleKey: 'predictive', groupKey: 'groupPredictive', keywords: 'simulador simulator preditivo predictive projecao projection cenario scenario' },
  { title: 'Sobre', url: '/about', group: 'Mais', titleKey: 'about', groupKey: 'groupAbout', keywords: 'sobre about ajuda help info dashboard' },
];

/**
 * Fase 3 IA enxuta: aliases de rotas antigas/prováveis (não 404).
 * O catch-all `*` já redireciona para `/`, mas o alias preserva a
 * intenção de navegação. `App.tsx` renderiza cada alias como
 * `<Navigate to={to} replace />`. Tabela intencionalmente pequena —
 * adicione entradas só com evidência de uso (YAGNI).
 */
export interface LegacyRedirect {
  from: string;
  to: string;
}

export const legacyRedirects: LegacyRedirect[] = [
  { from: '/home', to: '/overview' },
  { from: '/dashboard', to: '/overview' },
  { from: '/initiatives', to: '/initiative-analysis' },
  { from: '/agriculture', to: '/agricultural-analysis' },
  { from: '/simulator', to: '/predictive' },
  { from: '/sobre', to: '/about' },
];

/**
 * Resolve um alias legado para o destino canônico, ou `null` quando o
 * pathname não é alias. Lookup exato (sem normalização) — os aliases
 * são literais curtos e case-sensitive como as rotas do router.
 */
export function resolveLegacyRedirect(pathname: string): string | null {
  const hit = legacyRedirects.find((alias) => alias.from === pathname);
  return hit ? hit.to : null;
}

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
