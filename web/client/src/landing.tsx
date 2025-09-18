import './index.css'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { LandingPage } from '@/pages/LandingPage'

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('Failed to find the root element. Please ensure the HTML file contains an element with id="root".');
}

createRoot(rootElement).render(
  <StrictMode>
    <ErrorBoundary>
      <LandingPage />
    </ErrorBoundary>
  </StrictMode>,
)