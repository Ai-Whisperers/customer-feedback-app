import './index.css'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { AnalyzerPage } from '@/pages/AnalyzerPage'

// Debug logging
console.log('[Analyzer] Script loaded');
console.log('[Analyzer] Current URL:', window.location.href);

const rootElement = document.getElementById('root');
console.log('[Analyzer] Root element found:', !!rootElement);

if (!rootElement) {
  throw new Error('Failed to find the root element. Please ensure the HTML file contains an element with id="root".');
}

try {
  createRoot(rootElement).render(
    <StrictMode>
      <ErrorBoundary>
        <AnalyzerPage />
      </ErrorBoundary>
    </StrictMode>,
  );
  console.log('[Analyzer] Render call completed');
} catch (error) {
  console.error('[Analyzer] Error during render:', error);
}