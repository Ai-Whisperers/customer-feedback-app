/**
 * BFF (Backend for Frontend) server with API proxy.
 * Serves React app and proxies API calls to FastAPI backend.
 * No CORS complexity - everything goes through same origin.
 */

import express from 'express';
import compression from 'compression';
// import helmet from 'helmet'; // TEMPORARILY DISABLED
import path from 'path';
import dotenv from 'dotenv';
import { createProxyMiddleware } from 'http-proxy-middleware';

// Load environment variables
dotenv.config();

const app = express();
// Support both PORT and WEB_PORT for backward compatibility
const PORT = parseInt(process.env.PORT || process.env.WEB_PORT || '3000', 10);
const API_TARGET = process.env.API_PROXY_TARGET || 'http://localhost:8000';
const IS_PRODUCTION = process.env.NODE_ENV === 'production';

// Log configuration on startup
console.log(`[CONFIG] Starting server with:`);
console.log(`[CONFIG] PORT: ${PORT}`);
console.log(`[CONFIG] API_TARGET: ${API_TARGET}`);
console.log(`[CONFIG] NODE_ENV: ${process.env.NODE_ENV}`);
console.log(`[CONFIG] IS_PRODUCTION: ${IS_PRODUCTION}`);
console.log(`[CONFIG] HELMET DISABLED - DEBUGGING MODE`);

// Helmet completely disabled for debugging

// Compression for responses
app.use(compression());

// API Proxy MUST come before helmet CSP to avoid blocking
// API Proxy configuration
const apiProxy = createProxyMiddleware({
  target: API_TARGET,
  changeOrigin: true,
  secure: false, // IMPORTANT: Allow HTTP for internal services
  pathRewrite: {
    '^/api': '', // Remove /api prefix when forwarding
  },
  followRedirects: false, // Don't follow redirects
  on: {
    proxyReq: (proxyReq: any, req: any, res: any) => {
      console.log(`[PROXY] Forwarding ${req.method} ${req.path} to ${API_TARGET}`);
      console.log(`[PROXY] Target URL: ${proxyReq.protocol}//${proxyReq.host}${proxyReq.path}`);
      // Add custom headers if needed
      proxyReq.setHeader('X-Forwarded-Host', req.headers.host || '');
      proxyReq.setHeader('X-Real-IP', (req as any).ip || req.socket.remoteAddress || '');
      proxyReq.setHeader('X-Forwarded-Proto', 'http'); // Force HTTP for internal
    },
    proxyRes: (proxyRes: any, req: any, res: any) => {
      console.log(`[PROXY] Response ${proxyRes.statusCode} from ${req.path}`);
      // Log if there's a redirect
      if (proxyRes.statusCode >= 300 && proxyRes.statusCode < 400) {
        console.log(`[PROXY] Redirect detected:`, proxyRes.headers.location);
      }
    },
    error: (err: any, req: any, res: any) => {
      console.error('[PROXY ERROR] Details:', {
        path: req.path,
        target: API_TARGET,
        error: err.message,
        code: err.code,
        syscall: err.syscall
      });
      (res as any).status(502).json({
        error: 'Bad Gateway',
        message: 'Unable to connect to API service',
        details: IS_PRODUCTION ? undefined : err.message,
      });
    },
  },
  logger: console, // Always log in production for debugging
} as any);

// Proxy API requests BEFORE other middleware
app.use('/api', apiProxy);

// Helmet completely removed for debugging

// Request logging
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log(
      `[${new Date().toISOString()}] ${req.method} ${req.path} - ${res.statusCode} (${duration}ms)`
    );
  });
  next();
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'web-bff',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
});

// Debug endpoint to verify proxy configuration
app.get('/debug/proxy', (req, res) => {
  res.json({
    proxyEnabled: true,
    apiTarget: API_TARGET,
    helmetDisabled: true,
    environment: process.env.NODE_ENV,
    message: 'Proxy should be working. Try /api/health'
  });
});

// Note: API proxy moved before helmet to avoid CSP blocking

// Serve static files in production
if (IS_PRODUCTION) {
  // Client build is in dist/client from Vite build
  const buildPath = path.join(__dirname, '..', 'client');

  // Debug logging
  console.log('[DEBUG] Production mode activated');
  console.log('[DEBUG] __dirname:', __dirname);
  console.log('[DEBUG] buildPath:', buildPath);
  console.log('[DEBUG] buildPath exists:', require('fs').existsSync(buildPath));

  if (require('fs').existsSync(buildPath)) {
    const files = require('fs').readdirSync(buildPath);
    console.log('[DEBUG] Files in buildPath:', files.slice(0, 10));
  }

  // Serve static assets
  app.use(express.static(buildPath, {
    maxAge: '1d',
    setHeaders: (res, filepath) => {
      // Cache static assets for longer
      if (filepath.match(/\.(js|css|png|jpg|jpeg|gif|svg|ico)$/)) {
        res.setHeader('Cache-Control', 'public, max-age=86400');
      }
    },
  }));

  // SPA Routing - serve index.html for all routes (React Router)
  app.get('*', (req, res) => {
    const htmlPath = path.join(buildPath, 'index.html');
    console.log('[DEBUG] Serving SPA index.html from:', htmlPath);
    console.log('[DEBUG] File exists:', require('fs').existsSync(htmlPath));

    // Set no-cache headers for HTML to ensure fresh content
    res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
    res.setHeader('Pragma', 'no-cache');
    res.setHeader('Expires', '0');
    res.sendFile(htmlPath);
  });
} else {
  // Development mode - Vite handles static files
  app.get('/', (req, res) => {
    res.json({
      message: 'BFF Server running in development mode',
      note: 'Use Vite dev server on port 3001 for frontend development',
      api: `Proxying to ${API_TARGET}`,
    });
  });
}

// Error handling middleware
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Server error:', err);
  res.status(500).json({
    error: 'Internal Server Error',
    message: IS_PRODUCTION ? 'An error occurred' : err.message,
  });
});

// Start server - IMPORTANT: Bind to 0.0.0.0 for Render
const HOST = '0.0.0.0';
app.listen(PORT, HOST, () => {
  console.log(`
    ========================================
    BFF Server Started Successfully
    ========================================
    Host: ${HOST}
    Port: ${PORT}
    Environment: ${IS_PRODUCTION ? 'PRODUCTION' : 'DEVELOPMENT'}
    API Target: ${API_TARGET}
    Time: ${new Date().toISOString()}
    ========================================
  `);
});