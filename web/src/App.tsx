import { Routes, Route, Navigate } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import { UIProvider, DataProvider } from '@/contexts';
import { ThemeToggle } from '@/components/ThemeToggle';

// Lazy load pages
const LandingPage = lazy(() => import('@/pages/LandingPage').then(m => ({ default: m.LandingPage })));
const AboutPage = lazy(() => import('@/pages/AboutPage').then(m => ({ default: m.AboutPage })));
const AnalyzerPage = lazy(() => import('@/pages/AnalyzerPage').then(m => ({ default: m.AnalyzerPage })));

const LoadingFallback = () => (
  <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400 mx-auto"></div>
      <p className="mt-4 text-gray-600 dark:text-gray-300">Cargando página...</p>
    </div>
  </div>
);

export function App() {
  if (import.meta.env.DEV) console.log('[App] Rendering App component');

  return (
    <UIProvider>
      <DataProvider>
        {/* Global fixed controls - top right */}
        <div className="fixed top-4 right-4 z-50 flex gap-2">
          <ThemeToggle />
        </div>

        {/* Main content */}
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
          <Suspense fallback={<LoadingFallback />}>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="/analyzer" element={<AnalyzerPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Suspense>
        </div>
      </DataProvider>
    </UIProvider>
  );
}