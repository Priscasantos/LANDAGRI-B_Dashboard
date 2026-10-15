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
 * Rendered by `App.tsx` inside `<Routes>` with Suspense + ErrorBoundary.
 */
export const appRoutes: AppRoute[] = [
  { path: '/', Component: OverviewPage },
  { path: '/overview', Component: OverviewPage },
  { path: '/initiative-analysis/*', Component: InitiativeAnalysisPage },
  { path: '/agricultural-analysis/*', Component: AgriculturalAnalysisPage },
  { path: '/predictive', Component: PredictivePage },
  { path: '/about', Component: AboutPage },
];
