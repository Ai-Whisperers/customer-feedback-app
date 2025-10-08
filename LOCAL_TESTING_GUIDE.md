# Local Testing Guide
## Customer Feedback Analyzer - Browser Testing Setup

**Last Updated:** 2025-10-08
**Branch:** `refactor/optimization`
**Status:** Ready for testing after Redis setup

---

## Prerequisites

### Required
- [x] Python 3.12+ (installed)
- [x] Node.js 20+ (installed)
- [x] OpenAI API Key (configured in .env)
- [ ] **Redis Server** (required for Celery)

### Redis Setup Options

#### Option 1: Docker (Recommended for Windows)
```bash
# 1. Start Docker Desktop application
# 2. Run Redis container
docker run -d --name redis-local -p 6379:6379 redis:alpine

# 3. Verify Redis is running
docker ps | grep redis
```

#### Option 2: WSL (Windows Subsystem for Linux)
```bash
# In WSL terminal
sudo apt-get update
sudo apt-get install redis-server
sudo service redis-server start

# Verify
redis-cli ping  # Should return "PONG"
```

#### Option 3: Redis for Windows (Legacy)
Download from: https://github.com/tporadowski/redis/releases
Or use Memurai: https://www.memurai.com/

---

## Environment Configuration

### 1. Update .env for Local Development

Current `.env` points to production. For local testing, update these values:

```bash
# .env (modify these lines)
APP_ENV=development
DEBUG=true
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
API_PROXY_TARGET=http://localhost:8000
```

**Or** create a `.env.local` and use it:
```bash
cp .env.example .env.local
# Then edit .env.local with your OpenAI API key
```

### 2. Install Dependencies

```bash
# Backend
cd api
pip install -r requirements.txt

# Frontend
cd ../web
npm install
```

---

## Starting the Application

### Option A: Manual Start (3 Terminals)

**Terminal 1: FastAPI Backend**
```bash
cd api
uvicorn app.main:app --reload --port 8000
```
Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Terminal 2: Celery Worker**
```bash
cd api
celery -A app.workers.celery_app worker --loglevel=INFO --pool=solo
```
Note: Use `--pool=solo` on Windows

Expected output:
```
[tasks]
  . analyze_batch
  . analyze_feedback
  . cleanup_expired_tasks

celery@HOSTNAME ready.
```

**Terminal 3: Frontend + BFF**
```bash
cd web
npm run dev
```
Expected output:
```
  VITE v5.4.20  ready in 1234 ms

  ➜  Local:   http://localhost:3001/
  ➜  BFF:     http://localhost:3000/
```

### Option B: Using npm scripts (Parallel)

```bash
# In web/ directory
npm run dev:all
```
This starts all services concurrently

---

## Accessing the Application

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3001 | Main React app |
| **BFF Proxy** | http://localhost:3000 | Backend-for-Frontend proxy |
| **API Docs** | http://localhost:8000/docs | FastAPI Swagger UI |
| **API Health** | http://localhost:8000/api/health | Health check |

---

## Browser Testing Checklist

### 1. Basic Functionality
- [ ] Landing page loads
- [ ] About page accessible
- [ ] Theme toggle works (light/dark)
- [ ] Language switch works (ES/EN)

### 2. File Upload Flow
- [ ] Can select CSV/XLSX file
- [ ] File validation works (correct columns)
- [ ] Upload progress shows
- [ ] Task ID generated

### 3. Analysis Processing
- [ ] Progress updates show
- [ ] Deduplication message appears
- [ ] Batch progress displays
- [ ] Completion notification

### 4. Results Display
- [ ] Summary cards render
- [ ] NPS chart displays
- [ ] Emotions chart shows
- [ ] Pain points list appears
- [ ] Details table loads

### 5. Export Functionality
- [ ] CSV export downloads
- [ ] Excel basic export works
- [ ] Excel styled export works
- [ ] File naming correct

### 6. Error Handling
- [ ] Invalid file format rejected
- [ ] Missing columns detected
- [ ] Task timeout handled
- [ ] Network errors shown

---

## Test Data

### Small Test File (100 rows)
Located at: `test-data/sample_100.csv`

Columns:
```csv
Nota,Comentario Final,NPS
9,"Excelente servicio, muy rápido",promoter
6,"Lento pero funciona",detractor
8,"Bien en general",passive
```

### Medium Test File (1000 rows)
Generate with:
```python
# In api/
python scripts/generate_test_data.py --rows 1000 --output ../test-data/sample_1000.csv
```

---

## Troubleshooting

### Issue: Redis Connection Error
**Error:** `redis.exceptions.ConnectionError`

**Solutions:**
1. Verify Redis is running: `redis-cli ping`
2. Check Redis URL in .env: `redis://localhost:6379/0`
3. Restart Redis service
4. Check firewall/port 6379

### Issue: Celery Worker Not Starting
**Error:** `kombu.exceptions.OperationalError`

**Solutions:**
1. Ensure Redis is running
2. Use `--pool=solo` flag on Windows
3. Check CELERY_BROKER_URL in .env
4. Try: `celery -A app.workers.celery_app purge` (clears queue)

### Issue: Frontend Can't Connect to API
**Error:** `Network Error` or `CORS Error`

**Solutions:**
1. Verify API running on port 8000
2. Check API_PROXY_TARGET in .env
3. Restart BFF server (npm run dev)
4. Clear browser cache

### Issue: OpenAI API Error
**Error:** `AuthenticationError` or `RateLimitError`

**Solutions:**
1. Verify OPENAI_API_KEY in .env
2. Check API key is valid
3. Ensure sufficient credits
4. Reduce MAX_RPS if rate limited

### Issue: Build Errors
**Error:** TypeScript or Vite build errors

**Solutions:**
1. Delete node_modules and reinstall: `rm -rf node_modules && npm install`
2. Clear Vite cache: `rm -rf .vite`
3. Rebuild: `npm run build`

---

## Performance Monitoring

### Check Memory Usage
```bash
# Backend
python -c "from app.utils.memory_monitor import MemoryMonitor; print(f'{MemoryMonitor.get_used_memory_mb():.1f} MB')"

# Worker
celery -A app.workers.celery_app inspect stats
```

### Monitor Redis
```bash
# Connection count
redis-cli info clients | grep connected_clients

# Memory usage
redis-cli info memory | grep used_memory_human

# Active tasks
redis-cli keys "celery-task-meta-*" | wc -l
```

### API Response Times
```bash
# Using httpie
http GET localhost:8000/api/health --print=h

# Using curl
curl -w "\nTime: %{time_total}s\n" http://localhost:8000/api/health
```

---

## Next Steps After Testing

Once local testing is successful:

1. **Optional Polishing Items** (see POLISHING_TASKS.md)
   - Enhanced deduplication
   - Pandas optimization
   - Performance monitoring

2. **Documentation Updates** (see local-reports/)
   - Final optimization report
   - Deployment readiness checklist

3. **Deployment Preparation**
   - Environment variable validation
   - Production build testing
   - Render.com configuration

---

## Quick Reference

### Start Everything
```bash
# Terminal 1: Redis (Docker)
docker start redis-local

# Terminal 2: Backend + Worker
cd api
uvicorn app.main:app --reload & celery -A app.workers.celery_app worker --loglevel=INFO --pool=solo

# Terminal 3: Frontend
cd web
npm run dev
```

### Stop Everything
```bash
# Ctrl+C in each terminal, then:
docker stop redis-local
```

### Check Status
```bash
# Redis
docker ps | grep redis

# API
curl localhost:8000/api/health

# Frontend
curl localhost:3001
```

---

## Getting Help

- **Redis Issues:** Check Docker Desktop logs
- **API Issues:** Check `api/logs/` directory
- **Worker Issues:** Check Celery output in terminal
- **Frontend Issues:** Check browser console (F12)

**Architecture Tests:** `cd api && pytest tests/test_architecture.py -v`

**Export Tests:** `cd api && pytest tests/services/export/ -v`
