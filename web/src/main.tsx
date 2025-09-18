import './index.css';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import type { Root } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { App } from './App';

// Check if we're in development mode
const isDevelopment = process.env.NODE_ENV === 'development';

// Safe console wrapper that only logs in development
const safeLog = (message: string, ...args: any[]) => {
  if (isDevelopment) {
    console.log(message, ...args);
  }
};

// Safe error log that always logs (errors should always be visible)
const safeError = (message: string, ...args: any[]) => {
  console.error(message, ...args);
};

/**
 * Creates a safe fallback UI element without using innerHTML
 */
function createFallbackUI(message: string, details?: string): HTMLElement {
  const container = document.createElement('div');
  container.style.cssText = `
    padding: 40px;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    max-width: 600px;
    margin: 0 auto;
    text-align: center;
  `;

  const heading = document.createElement('h1');
  heading.textContent = 'Loading Error';
  heading.style.cssText = 'color: #dc2626; margin-bottom: 16px;';
  container.appendChild(heading);

  const paragraph = document.createElement('p');
  paragraph.textContent = message;
  paragraph.style.cssText = 'color: #4b5563; margin-bottom: 24px; font-size: 16px;';
  container.appendChild(paragraph);

  if (details && isDevelopment) {
    const detailsElem = document.createElement('details');
    detailsElem.style.cssText = 'margin: 20px 0; text-align: left;';

    const summary = document.createElement('summary');
    summary.textContent = 'Error Details';
    summary.style.cssText = 'cursor: pointer; padding: 8px; background: #f3f4f6; border-radius: 4px;';
    detailsElem.appendChild(summary);

    const pre = document.createElement('pre');
    pre.textContent = details;
    pre.style.cssText = `
      background: #1f2937;
      color: #f3f4f6;
      padding: 16px;
      border-radius: 4px;
      overflow-x: auto;
      margin-top: 8px;
      font-size: 12px;
    `;
    detailsElem.appendChild(pre);

    container.appendChild(detailsElem);
  }

  const button = document.createElement('button');
  button.textContent = 'Refresh Page';
  button.onclick = () => location.reload();
  button.style.cssText = `
    background: #3b82f6;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-size: 16px;
    cursor: pointer;
    margin-top: 16px;
  `;
  button.onmouseover = () => { button.style.background = '#2563eb'; };
  button.onmouseout = () => { button.style.background = '#3b82f6'; };

  container.appendChild(button);

  return container;
}

/**
 * Initialize the React application with Router
 */
function initApp() {
  const rootElement = document.getElementById('root');

  if (isDevelopment) {
    safeLog('[App] Root element found:', !!rootElement);
  }

  if (!rootElement) {
    safeError('[App] Root element #root not found!');

    const errorContainer = createFallbackUI(
      'Failed to initialize the application. The application container was not found.',
      'Expected element with id="root" but it was not found in the DOM.'
    );

    document.body.appendChild(errorContainer);
    return;
  }

  let root: Root | null = null;

  try {
    if (isDevelopment) {
      safeLog('[App] Creating React root...');
    }

    root = createRoot(rootElement);

    if (isDevelopment) {
      safeLog('[App] Rendering application...');
    }

    root.render(
      <StrictMode>
        <ErrorBoundary>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </ErrorBoundary>
      </StrictMode>
    );

    if (isDevelopment) {
      safeLog('[App] Render call completed successfully');
    }
  } catch (error) {
    safeError('[App] Error during render:', error);

    if (root) {
      try {
        root.unmount();
      } catch (unmountError) {
        safeError('[App] Error unmounting root:', unmountError);
      }
    }

    const errorMessage = error instanceof Error ? error.message : String(error);
    const errorStack = error instanceof Error ? error.stack : undefined;

    const errorUI = createFallbackUI(
      'An error occurred while loading the application.',
      errorStack || errorMessage
    );

    while (rootElement.firstChild) {
      rootElement.removeChild(rootElement.firstChild);
    }
    rootElement.appendChild(errorUI);
  }
}

// Ensure DOM is ready before initializing
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp, { once: true });
} else {
  queueMicrotask(initApp);
}