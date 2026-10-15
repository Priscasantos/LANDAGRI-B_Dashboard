import { Component, type ReactNode, type ErrorInfo } from 'react';
import { TriangleAlert } from 'lucide-react';
import { useT } from '../i18n/LanguageContext';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      const error = this.state.error;
      return <ErrorFallbackContent error={error} onRetry={() => this.setState({ hasError: false, error: null })} />;
    }
    return this.props.children;
  }
}

/** Fallback traduzido (Fase 1 i18n, namespace `errors`). */
function ErrorFallbackContent({ error, onRetry }: { error: Error | null; onRetry: () => void }): React.JSX.Element {
  const { t } = useT('errors');
  return (
    <div className="flex items-center justify-center min-h-[400px]" style={{ backgroundColor: 'var(--color-canvas)' }}>
      <div className="text-center max-w-md p-8">
        <div className="text-5xl mb-4" style={{ color: 'var(--color-error)' }}><TriangleAlert size={48} aria-hidden="true" className="inline-block" /></div>
        <h2 className="text-xl font-bold mb-2 text-fg">{t('boundaryTitle')}</h2>
        <p className="text-sm mb-4 text-fg-secondary">
          {error?.message || t('boundaryDefault')}
        </p>
        <button
          onClick={onRetry}
          className="px-4 py-2 text-white rounded-lg transition-colors"
          style={{ backgroundColor: 'var(--color-primary)' }}
          onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'var(--color-primary-hover)'; }}
          onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'var(--color-primary)'; }}
        >
          {t('boundaryRetry')}
        </button>
      </div>
    </div>
  );
}
