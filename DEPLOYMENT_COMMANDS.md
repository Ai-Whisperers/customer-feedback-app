# Deployment Commands for Production

## Pre-Deployment Checklist

### 1. Environment Variables Required
```bash
# Required in Render Dashboard for both API and Worker services:
OPENAI_API_KEY=sk-...
REDIS_URL=<provided by Render>
CELERY_BROKER_URL=${REDIS_URL}
CELERY_RESULT_BACKEND=${REDIS_URL}
```

### 2. Verify Local Setup
```bash
# Test Celery configuration
cd api
python -c "from app.workers.celery_app import celery_app; print('Celery configured')"

# Test API contract
python -c "from app.core.unified_aggregation import UnifiedAggregator; print('API contract valid')"

# Run tests
pytest tests/
```

## Deployment via Render

### Automatic Deployment
The repository is configured for automatic deployment via render.yaml:
```bash
# Push to main branch triggers deployment
git push origin main
```

### Manual Deployment Commands

#### 1. API Service (customer-feedback-api)
```bash
# Build
pip install -r api/requirements.txt

# Start command
cd api && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### 2. Celery Worker (celery-worker)
```bash
# Build
pip install -r api/requirements.txt

# Start command
cd api && celery -A app.workers.celery_app worker --loglevel=INFO

# With memory constraints for 512MB:
cd api && celery -A app.workers.celery_app worker \
  --loglevel=INFO \
  --concurrency=2 \
  --max-tasks-per-child=100 \
  --without-gossip \
  --without-mingle \
  --without-heartbeat
```

#### 3. Frontend (customer-feedback-app)
```bash
# Build
cd web && rm -rf node_modules dist && ./build.sh

# Start command
cd web && ./start.sh
```

## Monitoring Commands

### Check Celery Worker Status
```bash
# SSH into worker service, then:
celery -A app.workers.celery_app inspect active
celery -A app.workers.celery_app inspect stats
celery -A app.workers.celery_app inspect registered
```

### Monitor Memory Usage
```bash
# In worker logs, look for:
grep "memory_mb" /path/to/logs
grep "Memory status" /path/to/logs
```

### Check Redis Status
```bash
# Via Render dashboard or:
redis-cli -u $REDIS_URL ping
redis-cli -u $REDIS_URL info memory
```

## Troubleshooting

### If Worker Runs Out of Memory
1. Reduce CELERY_WORKER_CONCURRENCY to 1
2. Reduce MAX_BATCH_SIZE to 25
3. Enable more aggressive garbage collection

### If Tasks Are Not Being Processed
```bash
# Clear the queue
celery -A app.workers.celery_app purge

# Restart worker
# Via Render dashboard: Manual Deploy -> Restart Service
```

### If Frontend Can't Connect to API
1. Check API_PROXY_TARGET in web service environment
2. Verify it matches internal service URL: `http://customer-feedback-api-bmjp:10000`

## Performance Optimization Settings

### Current Production Settings (512MB RAM)
```env
# Worker settings optimized for 512MB
CELERY_WORKER_CONCURRENCY=2
MAX_BATCH_SIZE=50
MEMORY_WARNING_MB=400
MEMORY_CRITICAL_MB=450
HYBRID_ANALYSIS_ENABLED=true
ENABLE_PARALLEL_PROCESSING=true
```

### For Larger Instances (1GB+ RAM)
```env
CELERY_WORKER_CONCURRENCY=4
MAX_BATCH_SIZE=100
MEMORY_WARNING_MB=800
MEMORY_CRITICAL_MB=900
```

## Rollback Procedure

### Via Render Dashboard
1. Go to service Events tab
2. Find previous successful deploy
3. Click "Rollback to this deploy"

### Via Git
```bash
# Revert to previous commit
git revert HEAD
git push origin main

# Or reset to specific commit
git reset --hard <commit-hash>
git push --force origin main
```

## Health Checks

### API Health
```bash
curl https://your-api.onrender.com/health/simple
```

### Worker Health
Check logs for:
- "Celery worker ready"
- "Task analyze_feedback succeeded"
- No "CRITICAL" memory warnings

### Frontend Health
```bash
curl https://your-app.onrender.com/health
```

## Post-Deployment Verification

1. Upload test file (small CSV with 10-20 rows)
2. Check processing completes in < 30 seconds
3. Verify results display correctly
4. Test export functionality
5. Monitor logs for any errors

## Security Notes

- Never commit OPENAI_API_KEY to repository
- Use Render's secret management for sensitive vars
- API service should remain private (not public)
- Worker service should remain private
- Only frontend service should be public