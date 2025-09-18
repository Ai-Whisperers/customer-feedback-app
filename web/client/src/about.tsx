import './index.css'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { AboutPage } from '@/pages/AboutPage'

// Debug logging
console.log('[About] Script loaded');
console.log('[About] Current URL:', window.location.href);
console.log('[About] Document ready state:', document.readyState);

// Wait for DOM to be ready
function initApp() {
  const rootElement = document.getElementById('root');
  console.log('[About] Root element found:', !!rootElement);

  if (!rootElement) {
    console.error('[About] Root element not found!');
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
    console.log('[About] Creating React root...');
    const root = createRoot(rootElement);

    console.log('[About] Rendering components...');
    root.render(
      <StrictMode>
        <ErrorBoundary>
          <AboutPage />
        </ErrorBoundary>
      </StrictMode>,
    );
    console.log('[About] Render call completed');
  } catch (error) {
    console.error('[About] Error during render:', error);
    // Show error in UI instead of crashing
    rootElement.innerHTML = `
      <div style="padding: 20px; font-family: system-ui, -apple-system, sans-serif;">
        <h1>Application Error</h1>
        <p>An error occurred while loading the About page.</p>
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