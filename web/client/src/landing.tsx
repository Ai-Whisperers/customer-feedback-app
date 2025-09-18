import './index.css'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { LandingPage } from '@/pages/LandingPage'

// Debug logging
console.log('[Landing] Script loaded');
console.log('[Landing] Current URL:', window.location.href);
console.log('[Landing] Document ready state:', document.readyState);

// Wait for DOM to be ready
function initApp() {
  const rootElement = document.getElementById('root');
  console.log('[Landing] Root element found:', !!rootElement);

  if (!rootElement) {
    console.error('[Landing] Root element not found!');
    // Create a fallback UI
    document.body.innerHTML = `
      <div style="padding: 20px; font-family: system-ui, -apple-system, sans-serif;">
        <h1>Loading Error</h1>
        <p>Failed to initialize the application. Please refresh the page.</p>
        <button onclick="location.reload()">Refresh Page</button>
      </div>
    `;
    return;
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
    // Show error in UI instead of crashing
    rootElement.innerHTML = `
      <div style="padding: 20px; font-family: system-ui, -apple-system, sans-serif;">
        <h1>Application Error</h1>
        <p>An error occurred while loading the application.</p>
        <details>
          <summary>Error Details</summary>
          <pre>${error}</pre>
        </details>
        <button onclick="location.reload()" style="margin-top: 10px;">Refresh Page</button>
      </div>
    `;
  }
}

// Ensure DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}