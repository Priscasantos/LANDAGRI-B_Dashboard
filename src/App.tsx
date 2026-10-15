import { BrowserRouter, Routes, Route, useNavigate, type NavigateFunction } from 'react-router-dom';
import { Suspense, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from './contexts/ThemeContext';
import { ToastProvider } from './contexts/ToastContext';
import { SidebarConfigProvider } from './contexts/sidebar-context';
import ErrorBoundary from './components/ErrorBoundary';
import DashboardSkeleton from './components/ui/DashboardSkeleton';
import RootLayout from './layouts/RootLayout';
import { appRoutes, getBasename } from './config/routes';
import { useInitiatives } from './hooks/useInitiatives';

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

function AppContent(): React.JSX.Element {
  const navigate = useNavigate();

  // Restore path saved by the gh-pages SPA fallback (public/404.html).
  // Runs before the data gate below so deep links survive the redirect.
  useEffectRedirect(navigate);

  const { isLoading, error } = useInitiatives();

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-surface-alt">
        <div className="text-center max-w-md">
          <div className="text-4xl mb-4 text-error" role="img" aria-label="Aviso">⚠</div>
          <h2 className="text-xl font-bold mb-2 text-fg">Erro ao carregar dados</h2>
          <p className="text-fg-secondary">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <RootLayout>
      <Routes>
        {appRoutes.map(({ path, Component }) => (
          <Route
            key={path}
            path={path}
            element={
              <ErrorBoundary>
                <Suspense fallback={<DashboardSkeleton />}>
                  <Component />
                </Suspense>
              </ErrorBoundary>
            }
          />
        ))}
      </Routes>
    </RootLayout>
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
    const redirectPath = sessionStorage.getItem('redirectPath');
    if (redirectPath && redirectPath.startsWith('/') && redirectPath !== '/') {
      sessionStorage.removeItem('redirectPath');
      navigate(redirectPath, { replace: true });
    }
  }, [navigate]);
}

export default function App(): React.JSX.Element {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <ToastProvider>
          <QueryClientProvider client={queryClient}>
            <SidebarConfigProvider>
              <BrowserRouter basename={basename}>
                <AppContent />
              </BrowserRouter>
            </SidebarConfigProvider>
          </QueryClientProvider>
        </ToastProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}
