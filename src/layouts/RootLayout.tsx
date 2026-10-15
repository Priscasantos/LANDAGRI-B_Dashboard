import { Suspense, type ReactNode } from 'react';
import Header from '../components/Header';
import ErrorBoundary from '../components/ErrorBoundary';
import DashboardSkeleton from '../components/ui/DashboardSkeleton';

interface RootLayoutProps {
  children: ReactNode;
}

/**
 * App shell (shadcn-style base layout, adapted).
 * Preserves the existing Header + footer while moving layout sizing
 * from inline styles to Tailwind v4 tokens (`bg-canvas`,
 * `max-w-(--content-max-width)`). Each page keeps its own
 * Suspense fallback + ErrorBoundary (see `App.tsx` route mapping).
 */
export default function RootLayout({ children }: RootLayoutProps): React.JSX.Element {
  return (
    <div className="min-h-screen bg-canvas">
      <Header />
      <main className="w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8 max-w-(--content-max-width)">
        <ErrorBoundary>
          <Suspense fallback={<DashboardSkeleton />}>{children}</Suspense>
        </ErrorBoundary>
      </main>
      <footer className="border-t border-border py-6 mt-12 text-center text-xs text-fg-muted bg-surface-alt">
        <div className="w-full mx-auto px-4 sm:px-6 lg:px-8 max-w-(--content-max-width)">
          <p>© 2026 LANDAGRI-B Dashboard — Dados: MapBiomas & IBGE</p>
        </div>
      </footer>
    </div>
  );
}
