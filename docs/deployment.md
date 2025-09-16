# Deployment Guide

## Overview

The Customer AI Driven Feedback Analyzer is designed to be deployed on Render.com using their Blueprint infrastructure. The application consists of three services and one database.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Browser   │────▶│  Web (BFF)   │────▶│     API      │
└─────────────┘     └──────────────┘     └──────────────┘
                                               │     ▲
                                               ▼     │
                                          ┌──────────────┐
                                          │    Redis     │
                                          └──────────────┘
                                               ▲     │
                                               │     ▼
                                          ┌──────────────┐
                                          │   Worker     │
                                          └──────────────┘
```

## Services

### 1. API Service (feedback-analyzer-api)
- **Type**: Web Service
- **Runtime**: Python 3.11
- **Purpose**: REST API backend with FastAPI
- **Health Check**: `/api/health`
- **Plan**: Standard

### 2. Worker Service (feedback-analyzer-worker)
- **Type**: Worker Service
- **Runtime**: Python 3.11
- **Purpose**: Celery workers for async processing
- **Concurrency**: 2 workers
- **Plan**: Standard

### 3. Web Service (feedback-analyzer-web)
- **Type**: Web Service
- **Runtime**: Node.js 20
- **Purpose**: Serves React app and proxies API calls
- **Health Check**: `/health`
- **Plan**: Standard

### 4. Redis Database (feedback-analyzer-redis)
- **Type**: Redis
- **Purpose**: Task queue and result storage
- **Plan**: Starter
- **Eviction Policy**: allkeys-lru

## Environment Variables

### Required Secrets
```bash
OPENAI_API_KEY=sk-...  # Your OpenAI API key
```

### API Service Variables
- `PYTHON_VERSION=3.11`
- `AI_MODEL=gpt-4o-mini`
- `MAX_FILE_SIZE_MB=10`
- `ALLOWED_EXTENSIONS=csv,xlsx,xls`
- `MAX_BATCH_SIZE=50`
- `MAX_RPS=8`
- `TASK_EXPIRY_SECONDS=3600`

### Worker Service Variables
- Same as API service
- `CELERY_CONCURRENCY=2`

### Web Service Variables
- `NODE_VERSION=20`
- `NODE_ENV=production`
- `PORT=3000`

## Deployment Steps

### 1. Fork/Clone Repository
```bash
git clone <repository-url>
cd customer-feedback-app
```

### 2. Create Render Account
1. Sign up at https://render.com
2. Connect your GitHub account

### 3. Deploy with Blueprint
1. Go to Render Dashboard
2. Click "New" → "Blueprint"
3. Connect your repository
4. Render will detect `render.yaml` automatically
5. Add your `OPENAI_API_KEY` as a secret
6. Click "Apply"

### 4. Monitor Deployment
- Check service logs in Render dashboard
- Wait for all services to show "Live"
- Test health endpoints:
  - API: `https://<api-url>/api/health`
  - Web: `https://<web-url>/health`

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis (or Docker)

### Setup
```bash
# Install Python dependencies
cd api
pip install -r requirements.txt

# Install Node dependencies
cd ../web
npm install
cd client
npm install

# Start Redis
redis-server

# Start services (in separate terminals)
# Terminal 1 - API
cd api
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Worker
cd api
celery -A app.workers.celery_app worker --loglevel=info

# Terminal 3 - BFF Server
cd web
npm run dev

# Terminal 4 - React Dev Server
cd web/client
npm run dev
```

### Access Application
- Frontend: http://localhost:3001
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Monitoring

### Health Checks
All services expose health endpoints:
- API: `/api/health`
- Web: `/health`

### Logs
View logs in Render dashboard:
1. Navigate to service
2. Click "Logs" tab
3. Filter by time range or search

### Metrics
Monitor in Render dashboard:
- CPU usage
- Memory usage
- Request count
- Response times

## Scaling

### Horizontal Scaling
1. Go to service settings in Render
2. Adjust instance count
3. Apply changes

### Vertical Scaling
1. Go to service settings
2. Change plan (Starter → Standard → Pro)
3. Apply changes

### Redis Scaling
1. Upgrade Redis plan for more memory
2. Consider Redis cluster for high availability

## Troubleshooting

### Common Issues

#### 1. API Connection Errors
- Check `API_PROXY_TARGET` environment variable
- Verify API service is running
- Check network connectivity

#### 2. Task Processing Delays
- Check worker logs for errors
- Verify Redis connection
- Check OpenAI API key validity
- Monitor rate limits

#### 3. File Upload Failures
- Check file size limits
- Verify file format (CSV/Excel)
- Check API logs for validation errors

#### 4. Memory Issues
- Upgrade service plan
- Optimize batch sizes
- Implement pagination for large results

### Debug Commands
```bash
# Check API health
curl https://<api-url>/api/health

# Check Redis connection
redis-cli ping

# View Celery workers
celery -A app.workers.celery_app inspect active

# Check OpenAI API key
python -c "import openai; print('Valid' if openai.api_key else 'Invalid')"
```

## Security

### Best Practices
1. Never commit secrets to repository
2. Use Render's secret management
3. Enable HTTPS (automatic on Render)
4. Implement rate limiting
5. Regular dependency updates
6. Monitor for vulnerabilities

### API Security
- Input validation on all endpoints
- File type restrictions
- Size limits enforcement
- SQL injection prevention (using ORM)
- XSS protection (React handles this)

## Backup & Recovery

### Data Backup
- Redis data is ephemeral by design
- Results expire after 1 hour
- Consider external storage for permanent data

### Disaster Recovery
1. Re-deploy from GitHub
2. Restore environment variables
3. Services auto-recover on Render

## Cost Optimization

### Recommendations
1. Start with Starter plans
2. Monitor usage patterns
3. Scale based on actual needs
4. Use autoscaling for traffic spikes
5. Optimize batch processing sizes

### Estimated Costs (Monthly)
- API Service (Standard): $25
- Worker Service (Standard): $25
- Web Service (Standard): $25
- Redis (Starter): $7
- **Total**: ~$82/month

## Support

### Resources
- Render Documentation: https://docs.render.com
- FastAPI Documentation: https://fastapi.tiangolo.com
- React Documentation: https://react.dev
- OpenAI API Reference: https://platform.openai.com/docs

### Getting Help
1. Check service logs
2. Review error messages
3. Consult documentation
4. Contact Render support
5. Open GitHub issue