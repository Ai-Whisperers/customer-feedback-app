import { Component } from 'react';
import type { ReactNode, ErrorInfo } from 'react';
import { GlassCard, GlassButton } from './ui';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log error to error reporting service
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      error,
      errorInfo
    });
  }

  handleReset = (): void => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
    // Optionally reload the page
    if (window.location.pathname !== '/') {
      window.location.href = '/';
    }
  };

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen bg-gradient-to-br from-red-50 via-pink-50 to-purple-50 dark:from-gray-900 dark:via-red-900 dark:to-purple-900">
          <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
          <div className="relative z-10 container mx-auto px-4 py-8">
            <div className="max-w-2xl mx-auto">
              <GlassCard variant="gradient" padding="xl">
                <div className="text-center">
                  <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-red-100 dark:bg-red-900 flex items-center justify-center">
                    <svg
                      className="w-10 h-10 text-red-600 dark:text-red-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                      />
                    </svg>
                  </div>

                  <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-100 mb-4">
                    Algo salió mal
                  </h1>

                  <p className="text-lg text-gray-600 dark:text-gray-300 mb-8">
                    Lo sentimos, ha ocurrido un error inesperado.
                    Por favor, intenta recargar la página o volver al inicio.
                  </p>

                  {process.env.NODE_ENV === 'development' && this.state.error && (
                    <details className="mb-6 text-left">
                      <summary className="cursor-pointer text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
                        Detalles del error (solo en desarrollo)
                      </summary>
                      <div className="mt-2 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
                        <p className="text-sm font-mono text-red-600 dark:text-red-400 mb-2">
                          {this.state.error.toString()}
                        </p>
                        {this.state.errorInfo && (
                          <pre className="text-xs text-gray-600 dark:text-gray-400 overflow-auto max-h-64">
                            {this.state.errorInfo.componentStack}
                          </pre>
                        )}
                      </div>
                    </details>
                  )}

                  <div className="flex gap-4 justify-center">
                    <GlassButton
                      variant="primary"
                      size="lg"
                      onClick={() => window.location.reload()}
                    >
                      Recargar Página
                    </GlassButton>
                    <GlassButton
                      variant="secondary"
                      size="lg"
                      onClick={this.handleReset}
                    >
                      Volver al Inicio
                    </GlassButton>
                  </div>
                </div>
              </GlassCard>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}