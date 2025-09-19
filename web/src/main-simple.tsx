import './index.css';
import { createRoot } from 'react-dom/client';

console.log('[Simple] Starting simple app');

const rootEl = document.getElementById('root');
console.log('[Simple] Root element:', rootEl);

if (rootEl) {
  const root = createRoot(rootEl);
  root.render(
    <div style={{ padding: '40px', textAlign: 'center' }}>
      <h1>Simple Test App</h1>
      <p>If you can see this, React is working!</p>
    </div>
  );
  console.log('[Simple] App rendered');
} else {
  console.error('[Simple] Root element not found');
}