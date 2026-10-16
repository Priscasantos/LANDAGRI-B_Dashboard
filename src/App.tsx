import { BrowserRouter, Routes, Route, Navigate, useNavigate, type NavigateFunction } from 'react-router-dom';
import { Suspense, useEffect } from 'react';
import { TriangleAlert } from 'lucide-react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from './components/theme-provider';
import { ToastProvider } from './contexts/ToastContext';
import { SidebarConfigProvider } from './contexts/sidebar-context';
import ErrorBoundary from './components/ErrorBoundary';
import DashboardSkeleton from './components/ui/DashboardSkeleton';
import BaseLayout from './components/layout/BaseLayout';
import { appRoutes, getBasename, getRedirectPath, legacyRedirects, type AppRoute } from './config/routes';
import { useInitiatives } from './hooks/useInitiatives';
import { LanguageProvider, useT } from './i18n/LanguageContext';

/**
 * Shared QueryClient with minimal sane defaults.
 *
 * NOTE (Fase 3): no hook currently uses react-query — data loading goes
 * through `useInitiatives` (fetch + zustand store). The provider is kept
 * mounted so future queries get these defaults instead of retry storms:
 * no refetch on window focus, one retry, 60s stale time.
 */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const basename = getBasename();

/** Resolve título/descrição da rota no locale ativo (Fase 1 i18n). */
function LocalizedRoute({ route }: { route: AppRoute }): React.JSX.Element {
  const { t } = useT('nav');
  if (route.redirectTo) {
    return <Navigate to={route.redirectTo} replace />;
  }
  const Page = route.Component;
  return (
    <BaseLayout title={t(route.titleKey)} description={t(route.descriptionKey)}>
      <ErrorBoundary>
        <Suspense fallback={<DashboardSkeleton />}>
          <Page />
        </Suspense>
      </ErrorBoundary>
    </BaseLayout>
  );
}

function AppContent(): React.JSX.Element {
  const navigate = useNavigate();
  const { t } = useT('errors');

  // Restore path saved by the gh-pages SPA fallback (public/404.html).
  // Runs before the data gate below so deep links survive the redirect.
  useEffectRedirect(navigate);

  const { isLoading, error } = useInitiatives();

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-muted">
        <div className="text-center max-w-md">
          <div className="text-4xl mb-4 text-error" role="img" aria-label="Aviso"><TriangleAlert size={36} aria-hidden="true" className="inline-block" /></div>
          <h2 className="text-xl font-bold mb-2 text-foreground">{t('dataLoadTitle')}</h2>
          <p className="text-muted-foreground">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <Routes>
      {appRoutes.map((route) => (
        <Route
          key={route.path}
          path={route.path}
          element={<LocalizedRoute route={route} />}
        />
      ))}
      {/* Fase 3 IA enxuta: aliases PERMANENTES de rotas antigas (replace, não push/404).
          Ver `legacyRedirects` em config/routes — remoção quebra o teste de contrato. */}
      {legacyRedirects.map((alias) => (
        <Route key={alias.from} path={alias.from} element={<Navigate to={alias.to} replace />} />
      ))}
    </Routes>
  );
}

function useEffectRedirect(navigate: NavigateFunction): void {
  useEffect(() => {
    // Persist the active basename so public/404.html can redirect deep
    // links back here even under a custom VITE_BASENAME (see 404.html).
    try {
      localStorage.setItem('landagri-basename', basename);
    } catch {
      /* private mode: deep-link restore still works via path heuristic */
    }
    const redirectPath = getRedirectPath(sessionStorage);
    if (redirectPath) {
      navigate(redirectPath, { replace: true });
    }
  }, [navigate]);
}

export default function App(): React.JSX.Element {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <LanguageProvider>
          <ToastProvider>
            <QueryClientProvider client={queryClient}>
              <SidebarConfigProvider>
                <BrowserRouter basename={basename}>
                  <AppContent />
                </BrowserRouter>
              </SidebarConfigProvider>
            </QueryClientProvider>
          </ToastProvider>
        </LanguageProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}
