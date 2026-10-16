import type { CSSProperties } from 'react';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular' | 'card' | 'chart';
  width?: string | number;
  height?: string | number;
  count?: number;
}

export default function Skeleton({ className = '', variant = 'text', width, height, count = 1 }: SkeletonProps) {
  const baseClass = `animate-pulse rounded ${className}`;

  const variants: Record<string, string> = {
    text: 'h-4 rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
    card: 'h-32 rounded-xl',
    chart: 'h-80 rounded-xl',
  };

  const variantHeights: Record<string, number> = {
    text: 16,
    circular: 40,
    rectangular: 100,
    card: 128,
    chart: 320,
  };

  const style: CSSProperties = {
    backgroundColor: 'var(--color-border)',
    width: width || (variant === 'circular' ? 40 : '100%'),
    height: height ?? variantHeights[variant] ?? 16,
  };

  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={`${baseClass} ${variants[variant] ?? variants.text}`}
          style={style}
          aria-hidden="true"
        />
      ))}
    </>
  );
}

export function CardSkeleton() {
  return (
    <div
      className="p-5 rounded-xl bg-surface border border-border"
    >
      <Skeleton variant="text" width="60%" className="mb-3" />
      <Skeleton variant="text" width="40%" className="mb-2" />
      <Skeleton variant="text" width="80%" />
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div
      className="p-5 rounded-xl bg-surface border border-border"
    >
      <Skeleton variant="text" width="40%" className="mb-4" />
      <div className="flex items-end gap-2 h-64">
        {Array.from({ length: 8 }).map((_, i) => (
          <div
            key={i}
            className="flex-1 rounded-t animate-pulse"
            style={{
              height: `${30 + ((i * 17 + 5) % 71)}%`,
              backgroundColor: 'var(--color-border)',
            }}
          />
        ))}
      </div>
    </div>
  );
}

export function MetricCardSkeleton() {
  return (
    <div
      className="p-4 rounded-xl flex flex-col items-center min-h-[120px] bg-surface border border-border"
    >
      <Skeleton variant="circular" width={32} height={32} className="mb-2" />
      <Skeleton variant="text" width="60%" className="mb-1" />
      <Skeleton variant="text" width="40%" height={24} />
    </div>
  );
}
