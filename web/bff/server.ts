/**
 * BFF (Backend for Frontend) server with API proxy.
 * Serves React app and proxies API calls to FastAPI backend.
 * No CORS complexity - everything goes through same origin.
 */

import express from 'express';
import compression from 'compression';
import helmet from 'helmet';
import path from 'path';
import dotenv from 'dotenv';
import { createProxyMiddleware } from 'http-proxy-middleware';

// Load environment variables
dotenv.config();

const app = express();
const PORT = parseInt(process.env.PORT || '3000', 10);
const API_TARGET = process.env.API_PROXY_TARGET || 'http://localhost:8000';
const IS_PRODUCTION = process.env.NODE_ENV === 'production';

// Log configuration on startup
console.log(`[CONFIG] Starting server with:`);
console.log(`[CONFIG] PORT: ${PORT}`);
console.log(`[CONFIG] API_TARGET: ${API_TARGET}`);
console.log(`[CONFIG] NODE_ENV: ${process.env.NODE_ENV}`);
console.log(`[CONFIG] IS_PRODUCTION: ${IS_PRODUCTION}`);

// Security middleware with environment-aware CSP
const cspDirectives: any = IS_PRODUCTION ? {
  defaultSrc: ["'self'"],
  scriptSrc: [
    "'self'",
    "'unsafe-inline'",
    "'unsafe-eval'", // Required for Plotly
    "https://cdn.plot.ly" // Plotly CDN
  ],
  styleSrc: [
    "'self'",
    "'unsafe-inline'",
    "https://fonts.googleapis.com"
  ],
  imgSrc: ["'self'", "data:", "https:"],
  connectSrc: ["'self'", "https://cdn.plot.ly"],
  fontSrc: ["'self'", "https://fonts.gstatic.com"],
  objectSrc: ["'none'"],
  mediaSrc: ["'self'"],
  frameSrc: ["'none'"],
  workerSrc: ["'self'", "blob:"], // Allow web workers for better performance
  upgradeInsecureRequests: [], // Force HTTPS in production
} : {
  // More permissive in development
  defaultSrc: ["'self'"],
  scriptSrc: [
    "'self'",
    "'unsafe-inline'",
    "'unsafe-eval'",
    "https://cdn.plot.ly"
  ],
  styleSrc: [
    "'self'",
    "'unsafe-inline'",
    "https://fonts.googleapis.com"
  ],
  imgSrc: ["'self'", "data:", "https:"],
  connectSrc: ["'self'", "ws:", "wss:", "https://cdn.plot.ly"], // Allow WebSocket for HMR
  fontSrc: ["'self'", "https://fonts.gstatic.com"],
  objectSrc: ["'none'"],
  mediaSrc: ["'self'"],
  frameSrc: ["'none'"],
  workerSrc: ["'self'", "blob:"],
};

app.use(helmet({
  contentSecurityPolicy: {
    directives: cspDirectives,
  },
  // Additional security headers
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  },
  crossOriginEmbedderPolicy: false, // Allow embedding of resources
}));

// Compression for responses
app.use(compression());

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

// API Proxy configuration
const apiProxy = createProxyMiddleware({
  target: API_TARGET,
  changeOrigin: true,
  pathRewrite: {
    '^/api': '', // Remove /api prefix when forwarding
  },
  on: {
    proxyReq: (proxyReq: any, req: any, res: any) => {
      // Add custom headers if needed
      proxyReq.setHeader('X-Forwarded-Host', req.headers.host || '');
      proxyReq.setHeader('X-Real-IP', (req as any).ip || req.socket.remoteAddress || '');
    },
    error: (err: any, req: any, res: any) => {
      console.error('Proxy error:', err);
      (res as any).status(502).json({
        error: 'Bad Gateway',
        message: 'Unable to connect to API service',
        details: IS_PRODUCTION ? undefined : err.message,
      });
    },
  },
  logger: IS_PRODUCTION ? console : undefined,
} as any);

// Proxy API requests
app.use('/api', apiProxy);

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