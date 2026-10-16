import * as React from 'react';

/**
 * `prefers-reduced-motion: reduce` reativo (Expansão #4).
 *
 * A timeline animada usa este hook para desligar o autoplay quando o
 * usuário prefere movimento reduzido (o controle manual segue disponível).
 * Reversível: hook puro, sem estado global novo.
 */
export function usePrefersReducedMotion(): boolean {
  const [reduced, setReduced] = React.useState<boolean>(() =>
    typeof window !== 'undefined' && typeof window.matchMedia === 'function'
      ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
      : false,
  );

  React.useEffect(() => {
    if (typeof window.matchMedia !== 'function') return;
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    const handler = (e: MediaQueryListEvent): void => setReduced(e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);

  return reduced;
}
