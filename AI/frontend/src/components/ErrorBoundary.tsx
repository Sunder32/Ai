import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo,
    });

    // Здесь можно отправить ошибку в сервис мониторинга (Sentry, etc.)
    if (process.env.NODE_ENV === 'production') {
      // logErrorToService(error, errorInfo);
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 p-4">
          <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-red-500/30 p-8 max-w-2xl w-full">
            <div className="text-center mb-6">
              <h1 className="text-4xl font-bold text-red-400 mb-4">⚠️ Произошла ошибка</h1>
              <p className="text-white/80 text-lg mb-4">
                К сожалению, что-то пошло не так. Мы уже работаем над исправлением.
              </p>
            </div>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div className="bg-black/30 rounded-xl p-4 mb-6 max-h-96 overflow-auto">
                <p className="text-red-300 font-mono text-sm mb-2">
                  <strong>Ошибка:</strong> {this.state.error.toString()}
                </p>
                {this.state.errorInfo && (
                  <details className="text-white/60 font-mono text-xs">
                    <summary className="cursor-pointer text-cyan-400 hover:text-cyan-300 mb-2">
                      Показать детали
                    </summary>
                    <pre className="whitespace-pre-wrap">
                      {this.state.errorInfo.componentStack}
                    </pre>
                  </details>
                )}
              </div>
            )}

            <div className="flex gap-4 justify-center">
              <button
                onClick={this.handleReset}
                className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-semibold transition-all duration-300"
              >
                Попробовать снова
              </button>
              <button
                onClick={() => window.location.href = '/'}
                className="px-6 py-3 rounded-xl bg-white/10 hover:bg-white/20 border border-white/30 text-white font-semibold transition-all duration-300"
              >
                На главную
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
