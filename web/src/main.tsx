import './index.css';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { App } from './App';

console.log('[Main] Starting app initialization...');

const rootElement = document.getElementById('root');

if (!rootElement) {
  console.error('[Main] Root element not found!');
  document.body.innerHTML = '<h1>Error: Root element not found</h1>';
} else {
  console.log('[Main] Root element found, creating React root...');

  try {
    const root = createRoot(rootElement);
    console.log('[Main] React root created, rendering app...');

    root.render(
      <StrictMode>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </StrictMode>
    );

    console.log('[Main] App rendered successfully!');
  } catch (error) {
    console.error('[Main] Error rendering app:', error);
    rootElement.innerHTML = `<h1>Error rendering app</h1><pre>${error}</pre>`;
  }
}