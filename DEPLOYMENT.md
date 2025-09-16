# Deployment Guide - Customer AI Driven Feedback Analyzer

## Overview
This application is configured for deployment on Render.com with three services and a Redis database.

## Services Architecture

### 1. API Service (FastAPI)
- **Type**: Web service
- **Runtime**: Python 3.11
- **Build**: `api/build.sh`
- **Start**: `api/start.sh`
- **Health Check**: `/api/health`
- **Features**:
  - Handles file uploads and validation
  - Queues tasks to Celery
  - Serves analysis results
  - Rate limiting: 8 RPS, batch size: 50

### 2. Worker Service (Celery)
- **Type**: Worker service
- **Runtime**: Python 3.11
- **Build**: `api/build-worker.sh`
- **Start**: `api/start-worker.sh`
- **Concurrency**: 2 workers
- **Features**:
  - Processes feedback analysis tasks
  - Batch processing (50-100 rows)
  - OpenAI API integration
  - Auto-retry on failures

### 3. Web Service (BFF + React)
- **Type**: Web service
- **Runtime**: Node.js 20
- **Build**: `web/build.sh`
- **Start**: `web/start.sh`
- **Health Check**: `/health`
- **Features**:
  - React frontend (built with Vite)
  - Express BFF proxy server
  - No CORS issues (proxy pattern)
  - Static file serving

### 4. Redis Database
- **Type**: Managed Redis
- **Plan**: Starter
- **Policy**: allkeys-lru
- **Usage**:
  - Celery broker
  - Task results backend
  - 24-hour TTL for results

## Build Scripts

### API Build (`api/build.sh`)
1. Upgrades pip
2. Installs Python dependencies from requirements.txt
3. Verifies critical packages (FastAPI, Celery, OpenAI)
4. Tests app imports

### Worker Build (`api/build-worker.sh`)
1. Upgrades pip
2. Installs Python dependencies from requirements.txt
3. Verifies Celery and worker dependencies
4. Tests worker configuration

### Web Build (`web/build.sh`)
1. Installs root Node dependencies
2. Builds React client application
3. Compiles TypeScript server to CommonJS
4. Creates production dist folder
5. Installs production-only dependencies

## Start Scripts

### API Start (`api/start.sh`)
- Starts Uvicorn with FastAPI
- Configurable workers and log levels
- Health monitoring enabled

### Worker Start (`api/start-worker.sh`)
- Starts Celery worker with prefork pool
- Optimized for production (no heartbeat, gossip, mingle)
- Configurable concurrency and task limits

### Web Start (`web/start.sh`)
- Starts Node.js Express server
- Serves React build from dist folder
- Proxies API requests to backend

## Environment Variables

### Common
- `OPENAI_API_KEY`: Required for AI analysis
- `REDIS_URL`: Connection to Redis instance
- `AI_MODEL`: gpt-4o-mini (default)

### API Service
- `PORT`: Server port (default: 8000)
- `API_WORKERS`: Uvicorn workers (default: 1)
- `LOG_LEVEL`: Logging level (default: info)
- `MAX_BATCH_SIZE`: Max rows per batch (default: 50)
- `MAX_RPS`: Rate limit (default: 8)
- `TASK_EXPIRY_SECONDS`: Task TTL (default: 3600)

### Worker Service
- `CELERY_WORKER_CONCURRENCY`: Worker processes (default: 2)
- `CELERY_MAX_TASKS_PER_CHILD`: Task limit per worker (default: 100)
- `CELERY_LOG_LEVEL`: Logging level (default: info)

### Web Service
- `NODE_ENV`: Environment (production)
- `PORT`: Server port (default: 3000)
- `API_PROXY_TARGET`: Internal API URL (from Render)

## Deployment Steps

1. **Prepare Repository**
   ```bash
   # Verify deployment readiness
   bash verify-deployment.sh
   ```

2. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add deployment configuration for Render"
   git push origin main
   ```

3. **Deploy on Render**
   - Connect GitHub repository
   - Use `render.yaml` for blueprint deployment
   - Set `OPENAI_API_KEY` as secret
   - Deploy all services

4. **Verify Deployment**
   - Check API health: `https://[api-url]/api/health`
   - Check Web health: `https://[web-url]/health`
   - Test file upload functionality
   - Monitor worker logs for processing

## Performance Expectations

- **850-1200 rows**: 5-10 seconds
- **1800 rows**: ~18 seconds
- **3000 rows**: ~30 seconds
- Linear scaling with batch processing

## Troubleshooting

### Build Failures
- Check Python version (3.11 required)
- Check Node version (20+ required)
- Verify all dependencies in requirements.txt/package.json

### Runtime Issues
- Verify OPENAI_API_KEY is set
- Check Redis connection
- Monitor worker logs for errors
- Verify API_PROXY_TARGET is correct

### Performance Issues
- Adjust CELERY_WORKER_CONCURRENCY
- Tune MAX_BATCH_SIZE for optimal throughput
- Monitor Redis memory usage

## Security Notes

- All secrets in environment variables
- No CORS enabled (proxy pattern)
- File size limit: 20MB
- Supported formats: CSV, XLSX, XLS only
- Results expire after 24 hours

## Monitoring

- API logs: Uvicorn access and error logs
- Worker logs: Celery task execution logs
- Web logs: Express server and proxy logs
- Redis: Memory usage and connection stats

## Maintenance

- Regular dependency updates
- Monitor OpenAI API usage and costs
- Clear old Redis keys if needed
- Review and optimize batch sizes based on usage