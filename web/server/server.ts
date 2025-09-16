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
const PORT = process.env.PORT || 3000;
const API_TARGET = process.env.API_PROXY_TARGET || 'http://localhost:8000';
const IS_PRODUCTION = process.env.NODE_ENV === 'production';

// Security middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'"],
      fontSrc: ["'self'"],
      objectSrc: ["'none'"],
      mediaSrc: ["'self'"],
      frameSrc: ["'none'"],
    },
  },
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
  onProxyReq: (proxyReq, req, res) => {
    // Add custom headers if needed
    proxyReq.setHeader('X-Forwarded-Host', req.headers.host || '');
    proxyReq.setHeader('X-Real-IP', req.ip || '');
  },
  onError: (err, req, res) => {
    console.error('Proxy error:', err);
    res.status(502).json({
      error: 'Bad Gateway',
      message: 'Unable to connect to API service',
      details: IS_PRODUCTION ? undefined : err.message,
    });
  },
  logLevel: IS_PRODUCTION ? 'error' : 'debug',
});

// Proxy API requests
app.use('/api', apiProxy);

// Serve static files in production
if (IS_PRODUCTION) {
  const buildPath = path.join(__dirname, '..', 'dist');

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

  // Serve index.html for all non-API routes (React Router support)
  app.get('*', (req, res) => {
    res.sendFile(path.join(buildPath, 'index.html'));
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

// Start server
app.listen(PORT, () => {
  console.log(`
    ========================================
    BFF Server Started Successfully
    ========================================
    Port: ${PORT}
    Environment: ${IS_PRODUCTION ? 'PRODUCTION' : 'DEVELOPMENT'}
    API Target: ${API_TARGET}
    Time: ${new Date().toISOString()}
    ========================================
  `);
});