import './index.css';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { App } from './App';

if (import.meta.env.DEV) console.log('[Main] Starting app initialization...');

const rootElement = document.getElementById('root');

if (!rootElement) {
  if (import.meta.env.DEV) console.error('[Main] Root element not found!');
  document.body.innerHTML = '<h1>Error: Root element not found</h1>';
} else {
  if (import.meta.env.DEV) console.log('[Main] Root element found, creating React root...');

  try {
    const root = createRoot(rootElement);
    if (import.meta.env.DEV) console.log('[Main] React root created, rendering app...');

    root.render(
      <StrictMode>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </StrictMode>
    );

    if (import.meta.env.DEV) console.log('[Main] App rendered successfully!');
  } catch (error) {
    if (import.meta.env.DEV) console.error('[Main] Error rendering app:', error);
    rootElement.innerHTML = `<h1>Error rendering app</h1><pre>${error}</pre>`;
  }
}