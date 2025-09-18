import './index.css'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { AboutPage } from '@/pages/AboutPage'

// Debug logging
console.log('[About] Script loaded');
console.log('[About] Current URL:', window.location.href);

const rootElement = document.getElementById('root');
console.log('[About] Root element found:', !!rootElement);

if (!rootElement) {
  throw new Error('Failed to find the root element. Please ensure the HTML file contains an element with id="root".');
}

try {
  createRoot(rootElement).render(
    <StrictMode>
      <ErrorBoundary>
        <AboutPage />
      </ErrorBoundary>
    </StrictMode>,
  );
  console.log('[About] Render call completed');
} catch (error) {
  console.error('[About] Error during render:', error);
}