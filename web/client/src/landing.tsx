import './index.css'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { LandingPage } from '@/pages/LandingPage'

// Debug logging
console.log('[Landing] Script loaded');
console.log('[Landing] Current URL:', window.location.href);
console.log('[Landing] Document ready state:', document.readyState);

const rootElement = document.getElementById('root');
console.log('[Landing] Root element found:', !!rootElement);

if (!rootElement) {
  console.error('[Landing] Root element not found!');
  throw new Error('Failed to find the root element. Please ensure the HTML file contains an element with id="root".');
}

try {
  console.log('[Landing] Creating React root...');
  const root = createRoot(rootElement);

  console.log('[Landing] Rendering components...');
  root.render(
    <StrictMode>
      <ErrorBoundary>
        <LandingPage />
      </ErrorBoundary>
    </StrictMode>,
  );
  console.log('[Landing] Render call completed');
} catch (error) {
  console.error('[Landing] Error during render:', error);
  throw error;
}