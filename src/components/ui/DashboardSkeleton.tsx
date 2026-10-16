import Skeleton from './Skeleton';

export default function DashboardSkeleton() {
  return (
    <div className="min-h-screen bg-canvas">
      {/* Header skeleton */}
      <header className="sticky top-0 z-40 bg-surface border-b border-border shadow-sm">
        <div className="flex items-center justify-between h-14 px-6">
          <div className="flex items-center gap-3">
            <Skeleton className="w-8 h-8 rounded-lg" />
            <Skeleton className="h-4 w-32" />
          </div>
          <div className="flex items-center gap-4">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-16" />
            <Skeleton className="h-4 w-16" />
          </div>
          <Skeleton className="w-8 h-8 rounded-full" />
        </div>
      </header>

      {/* Main content skeletons */}
      <main className="w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8" style={{ maxWidth: '1600px' }}>
        {/* Cards grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="rounded-xl p-5 bg-surface border border-border">
              <Skeleton className="h-3 w-24 mb-3" />
              <Skeleton className="h-8 w-20 mb-2" />
              <Skeleton className="h-3 w-32" />
            </div>
          ))}
        </div>

        {/* Two column layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="rounded-xl p-5 bg-surface border border-border">
            <Skeleton className="h-5 w-40 mb-4" />
            <Skeleton className="h-3 w-full mb-2" />
            <Skeleton className="h-3 w-3/4 mb-2" />
            <Skeleton className="h-3 w-5/6 mb-2" />
            <Skeleton className="h-3 w-2/3" />
          </div>
          <div className="rounded-xl p-5 bg-surface border border-border">
            <Skeleton className="h-5 w-40 mb-4" />
            <Skeleton className="h-3 w-full mb-2" />
            <Skeleton className="h-3 w-3/4 mb-2" />
            <Skeleton className="h-3 w-5/6 mb-2" />
            <Skeleton className="h-3 w-2/3" />
          </div>
        </div>

        {/* Bottom section */}
        <div className="mt-8 rounded-xl p-5 bg-surface border border-border">
          <Skeleton className="h-5 w-48 mb-4" />
          <div className="h-[300px] rounded-lg bg-surface-alt" />
        </div>
      </main>

      {/* Footer skeleton */}
      <footer className="border-t border-border py-6 mt-12">
        <div className="w-full mx-auto px-4 sm:px-6 lg:px-8 flex justify-center" style={{ maxWidth: '1600px' }}>
          <Skeleton className="h-3 w-64" />
        </div>
      </footer>
    </div>
  );
}
