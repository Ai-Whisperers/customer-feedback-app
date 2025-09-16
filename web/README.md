# Web Service - Customer Feedback Analyzer

## Overview
This is the web service for the Customer Feedback Analyzer, containing both the React frontend application and the Node.js BFF (Backend for Frontend) server.

## Architecture

### Structure
```
web/
├── client/           # React + TypeScript frontend application
│   ├── src/         # Source code
│   │   ├── components/   # UI components
│   │   ├── lib/         # API client and utilities
│   │   └── App.tsx      # Main application component
│   ├── package.json     # Frontend dependencies
│   └── vite.config.ts   # Vite configuration
│
├── server/          # Node.js BFF server
│   └── server.ts    # Express server with API proxy
│
└── package.json     # Server dependencies and scripts
```

### Key Design Decisions
1. **No CORS Issues**: BFF proxy pattern eliminates CORS complexity
2. **Single Origin**: All requests go through the same origin (port 3000)
3. **Clean Separation**: Frontend (client/) and BFF (server/) are separate
4. **Production Ready**: Optimized build process for Render deployment

## Development Setup

### Prerequisites
- Node.js >= 18.0.0
- npm or yarn

### Installation
```bash
# Install server dependencies
npm install

# Install client dependencies
cd client && npm install
```

### Development Mode
Run both the BFF server and React dev server:

```bash
# Terminal 1: Start BFF server (port 3000)
npm run server

# Terminal 2: Start React dev server (port 3001)
npm run dev:client
```

Access the application at http://localhost:3001

### API Proxy Flow
1. React app (port 3001) → `/api/*` requests
2. Vite proxy → BFF server (port 3000)
3. BFF server → FastAPI backend (port 8000)
4. Response flows back through the same chain

## Production Build

### Build Process
```bash
# Build everything for production
npm run build
```

This command:
1. Installs client dependencies
2. Builds the React app (output: client/dist)
3. Compiles the TypeScript server
4. Copies client build to dist/client-build

### Run Production Build
```bash
npm run start:prod
```

## Environment Variables

### Required for Production
```env
PORT=3000                                    # Server port
API_PROXY_TARGET=https://api-service.com    # Backend API URL
NODE_ENV=production                         # Production mode
```

### Development Defaults
```env
PORT=3000                         # BFF server port
API_PROXY_TARGET=http://localhost:8000    # Local FastAPI
```

## API Client Configuration

The frontend uses a centralized API client (`client/src/lib/api.ts`) that:
- Routes all requests through `/api` prefix
- Handles error responses consistently
- Provides TypeScript types for all endpoints
- Manages file uploads and result polling

### Available Endpoints
- `POST /api/upload` - Upload feedback file
- `GET /api/status/:taskId` - Check processing status
- `GET /api/results/:taskId` - Get analysis results
- `GET /api/export/:taskId` - Export results as CSV/XLSX
- `GET /api/health` - Health check

## Deployment (Render)

### Service Configuration
```yaml
services:
  - type: web
    name: feedback-analyzer-web
    env: node
    buildCommand: npm run build:render
    startCommand: npm run start:prod
    envVars:
      - key: API_PROXY_TARGET
        fromService:
          name: feedback-analyzer-api
          type: web
          property: hostport
```

### Build Scripts
- `build:render` - Optimized for Render's build environment
- `start:prod` - Production server startup

## Common Issues & Solutions

### Issue: API connection fails
**Solution**: Verify API_PROXY_TARGET is set correctly

### Issue: Static files not served in production
**Solution**: Ensure client build is in dist/client-build

### Issue: Development proxy not working
**Solution**: Check that BFF server is running on port 3000

## Scripts Reference

| Script | Description |
|--------|-------------|
| `npm run dev` | Start BFF server with hot reload |
| `npm run dev:client` | Start React dev server |
| `npm run build` | Build for production |
| `npm run build:render` | Build for Render deployment |
| `npm run start:prod` | Run production server |
| `npm run lint` | Run ESLint on client code |
| `npm run type-check` | TypeScript type checking |