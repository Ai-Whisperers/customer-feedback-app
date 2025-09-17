# Service Integration Guide - Customer Feedback Analyzer

## Architecture Overview

The application consists of two separate services that communicate via HTTP:

```
┌─────────────┐     HTTP/API     ┌─────────────┐
│   Web BFF   │ ──────────────▶  │  FastAPI    │
│   (Node.js) │                   │   Backend   │
│   Port 3000 │                   │  Port 8000  │
└─────────────┘                   └─────────────┘
       │                                 │
       │                                 │
       ▼                                 ▼
┌─────────────┐                   ┌─────────────┐
│   React     │                   │   Celery    │
│   Client    │                   │   Worker    │
└─────────────┘                   └─────────────┘
                                         │
                                         ▼
                                  ┌─────────────┐
                                  │    Redis    │
                                  │   Broker    │
                                  └─────────────┘
```

## Service Configuration

### 1. Web Service (Frontend + BFF)

**Location:** `/web`
**Port:** 3000
**Purpose:** Serves React frontend and proxies API requests

#### Environment Variables (web/.env)
```bash
PORT=3000
NODE_ENV=development
API_PROXY_TARGET=http://localhost:8000  # Points to API service
```

#### Key Files:
- `web/server/server.ts` - BFF proxy server
- `web/client/src/lib/api.ts` - API client
- All API calls use `/api` prefix which gets proxied to backend

### 2. API Service (Backend)

**Location:** `/api`
**Port:** 8000
**Purpose:** FastAPI backend with AI analysis

#### Environment Variables (api/.env)
```bash
APP_ENV=development
PORT=8000
OPENAI_API_KEY=sk-xxx  # Required for AI analysis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
SECRET_KEY=your-secret-key-min-32-chars
```

#### API Endpoints:
- `GET /` - API info
- `GET /health` - Health check
- `POST /upload` - Upload CSV/XLSX file
- `GET /status/{task_id}` - Check processing status
- `GET /results/{task_id}` - Get analysis results
- `GET /export/{task_id}` - Export results

## Running Services Locally

### Prerequisites
1. **Redis** - Required for Celery task queue
   ```bash
   # Install Redis (Windows - using WSL or Docker)
   docker run -p 6379:6379 redis:alpine

   # Or on Mac/Linux
   brew install redis
   redis-server
   ```

2. **Environment Files**
   ```bash
   # Copy examples and configure
   cp web/.env.example web/.env
   cp api/.env.example api/.env

   # Edit api/.env and add your OPENAI_API_KEY
   ```

### Start Services

#### Terminal 1 - API Backend:
```bash
cd api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Terminal 2 - Celery Worker:
```bash
cd api
celery -A app.workers.celery_app worker --loglevel=INFO
```

#### Terminal 3 - Web BFF:
```bash
cd web
npm install
npm run dev  # Runs BFF server on port 3000
```

#### Terminal 4 - React Dev Server (optional):
```bash
cd web/client
npm install
npm run dev  # Runs on port 3001 with HMR
```

## Testing Integration

### Run Integration Tests:
```bash
node test-integration.js
```

### Manual Testing:

1. **Test API Health:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Test Web Proxy:**
   ```bash
   curl http://localhost:3000/api/health
   ```

3. **Test File Upload via Proxy:**
   ```bash
   curl -X POST http://localhost:3000/api/upload \
     -F "file=@test.csv"
   ```

## Common Issues & Solutions

### Issue 1: Services Can't Connect
**Symptom:** "Bad Gateway" or "ECONNREFUSED"
**Solution:**
- Ensure API is running on port 8000
- Check `API_PROXY_TARGET` in web/.env
- Verify no firewall blocking localhost connections

### Issue 2: File Upload Fails
**Symptom:** Upload returns error
**Solution:**
- Check OPENAI_API_KEY is set in api/.env
- Ensure Redis is running
- Verify Celery worker is active

### Issue 3: CORS Errors
**Symptom:** CORS policy blocks requests
**Solution:**
- API shouldn't have CORS (it's private)
- All requests should go through web proxy at `/api`
- Never call API directly from browser

## Production Deployment (Render)

### Service Configuration on Render:

#### Web Service (Public):
```yaml
Type: Web Service
Build Command: cd web && npm run build:render
Start Command: cd web && npm run start:prod
Environment:
  - PORT: 3000
  - NODE_ENV: production
  - API_PROXY_TARGET: https://your-api.onrender.com
```

#### API Service (Private):
```yaml
Type: Private Service
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port 8000
Environment:
  - APP_ENV: production
  - OPENAI_API_KEY: [secret]
  - REDIS_URL: [Redis cloud URL]
  - SECRET_KEY: [secret]
```

#### Worker Service (Private):
```yaml
Type: Background Worker
Build Command: pip install -r requirements.txt
Start Command: celery -A app.workers.celery_app worker
Environment:
  - Same as API service
```

## Security Considerations

1. **API is Private**: Never expose API directly to internet
2. **Use BFF Proxy**: All API calls go through web proxy
3. **Environment Separation**: Services don't share secrets
4. **No CORS on API**: API only accepts calls from BFF
5. **Secret Management**: Use Render's secret management for production

## Monitoring & Logs

### Check Service Health:
- Web: `http://your-app.com/health`
- API (via proxy): `http://your-app.com/api/health`

### View Logs:
- Local: Check terminal output
- Render: Use Render dashboard logs

### Debug Connection Issues:
1. Check both services are running
2. Verify environment variables
3. Test with integration script
4. Check network connectivity
5. Review proxy configuration

## Support

For issues, check:
1. Service logs for errors
2. Environment variable configuration
3. Network connectivity between services
4. Redis availability
5. OpenAI API key validity