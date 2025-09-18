/**
 * Unified bootstrap utility for MPA React applications
 * Provides safe DOM initialization and error handling
 */

import React, { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import type { Root } from 'react-dom/client';
import { ErrorBoundary } from '@/components/ErrorBoundary';

interface BootstrapOptions {
  pageName: string;
  component: React.ComponentType;
  rootElementId?: string;
  enableDebugLogs?: boolean;
}

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
 * Bootstrap a React application safely
 */
export function bootstrapApp(options: BootstrapOptions): void {
  const {
    pageName,
    component: Component,
    rootElementId = 'root',
    enableDebugLogs = isDevelopment
  } = options;

  // Setup debug logging if enabled
  if (enableDebugLogs) {
    safeLog(`[${pageName}] Script loaded`);
    safeLog(`[${pageName}] Current URL:`, window.location.href);
    safeLog(`[${pageName}] Document ready state:`, document.readyState);
  }

  function initApp() {
    const rootElement = document.getElementById(rootElementId);

    if (enableDebugLogs) {
      safeLog(`[${pageName}] Root element found:`, !!rootElement);
    }

    if (!rootElement) {
      safeError(`[${pageName}] Root element '#${rootElementId}' not found!`);

      // Create a container for the error message instead of replacing body.innerHTML
      const errorContainer = createFallbackUI(
        `Failed to initialize ${pageName}. The application container was not found.`,
        `Expected element with id="${rootElementId}" but it was not found in the DOM.`
      );

      // Append to body instead of replacing innerHTML
      document.body.appendChild(errorContainer);
      return;
    }

    let root: Root | null = null;

    try {
      if (enableDebugLogs) {
        safeLog(`[${pageName}] Creating React root...`);
      }

      root = createRoot(rootElement);

      if (enableDebugLogs) {
        safeLog(`[${pageName}] Rendering components...`);
      }

      root.render(
        <StrictMode>
          <ErrorBoundary>
            <Component />
          </ErrorBoundary>
        </StrictMode>
      );

      if (enableDebugLogs) {
        safeLog(`[${pageName}] Render call completed successfully`);
      }
    } catch (error) {
      safeError(`[${pageName}] Error during render:`, error);

      // If root was created, unmount it properly
      if (root) {
        try {
          root.unmount();
        } catch (unmountError) {
          safeError(`[${pageName}] Error unmounting root:`, unmountError);
        }
      }

      // Create error UI safely without innerHTML
      const errorMessage = error instanceof Error ? error.message : String(error);
      const errorStack = error instanceof Error ? error.stack : undefined;

      const errorUI = createFallbackUI(
        `An error occurred while loading ${pageName}.`,
        errorStack || errorMessage
      );

      // Clear the root element and append error UI
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
    // DOM is already ready, init immediately
    // Use microtask to ensure any pending DOM operations complete
    queueMicrotask(initApp);
  }
}

/**
 * Utility to wait for DOM ready state
 */
export function whenDOMReady(): Promise<void> {
  return new Promise((resolve) => {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => resolve(), { once: true });
    } else {
      resolve();
    }
  });
}

/**
 * Check if the app is running in production
 */
export function isProduction(): boolean {
  return process.env.NODE_ENV === 'production';
}

// Export development flag for convenience
export { isDevelopment };