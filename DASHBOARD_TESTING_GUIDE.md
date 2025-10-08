# Token Metrics Dashboard - Testing Guide

**Created:** 2025-10-08
**Feature:** Real-time OpenAI token consumption dashboard
**Status:** Ready for testing

---

## Overview

A new real-time dashboard has been implemented to monitor OpenAI API token usage and costs. This allows you to:

- **Track token consumption** in real-time
- **Monitor costs** for GPT-4o-mini API usage
- **View metrics** per task and globally
- **Analyze patterns** in hourly/daily usage

---

## Quick Start

### 1. Prerequisites

Ensure you have:
- ✅ OpenAI API key in `.env` file
- ✅ Redis running (Docker, WSL, or local)
- ✅ All dependencies installed

### 2. Start Services

**Terminal 1: Start Redis** (if not running)
```bash
docker run -d --name redis-local -p 6379:6379 redis:alpine
```

**Terminal 2: Start API**
```bash
cd api
uvicorn app.main:app --reload --port 8000
```

**Terminal 3: Start Celery Worker**
```bash
cd api
celery -A app.workers.celery_app worker --loglevel=INFO --pool=solo
```

**Terminal 4: Start Frontend** (optional, for full testing)
```bash
cd web
npm run dev
```

### 3. Access Dashboard

**Open your browser:**
```
http://localhost:8000/api/metrics/dashboard
```

You should see a beautiful purple dashboard with real-time metrics!

---

## Dashboard Features

### Main Metrics Cards

| Metric | Description |
|--------|-------------|
| **Total Tokens** | Cumulative tokens used since metrics started |
| **Total Cost** | Actual cost in USD based on GPT-4o-mini pricing |
| **Comments Analyzed** | Total number of comments processed |
| **Avg Tokens/Comment** | Average token usage per comment |

### Token Breakdown Section

Shows detailed breakdown of:
- **Input Tokens (Prompts)** - Tokens sent to OpenAI
- **Output Tokens (Completions)** - Tokens received from OpenAI
- **Total Requests** - Number of API calls made
- **Total Batches** - Number of batches processed

### Last Hour Stats

Quick view of activity in the last 60 minutes:
- Tokens used
- Cost incurred
- Comments processed

### Pricing Information

Current GPT-4o-mini pricing:
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens

### Cost Estimates

Projected costs for:
- Per 1,000 comments
- Per 10,000 comments

Based on current average token usage per comment.

---

## API Endpoints

### 1. Dashboard UI (HTML)
```
GET /api/metrics/dashboard
```
Returns the full HTML dashboard with auto-refresh.

### 2. Metrics Summary (JSON)
```
GET /api/metrics/summary
```
Returns JSON with complete metrics data:
```json
{
  "timestamp": "2025-10-08T12:00:00",
  "global": {
    "total_tokens": 15000,
    "total_cost_usd": 0.0123,
    "total_comments": 250,
    "avg_tokens_per_comment": 60,
    ...
  },
  "last_hour": { ... },
  "last_24_hours": { ... },
  "pricing": { ... }
}
```

### 3. Task-Specific Metrics
```
GET /api/metrics/task/{task_id}
```
Get metrics for a specific analysis task.

### 4. Recent Metrics
```
GET /api/metrics/recent?hours=6
```
Get aggregated metrics for the last N hours.

### 5. Reset Metrics (Admin)
```
POST /api/metrics/reset
```
⚠️ Resets all metrics. Use with caution!

---

## Testing Workflow

### Basic Test (Manual)

1. **Start all services** (see Quick Start above)

2. **Open dashboard**
   ```
   http://localhost:8000/api/metrics/dashboard
   ```
   Should show all zeros initially.

3. **Upload a test file** via frontend:
   ```
   http://localhost:3001
   ```
   - Create a small CSV with 10-20 rows
   - Upload and wait for processing

4. **Watch dashboard update** in real-time
   - Tokens should increment
   - Cost should calculate
   - Comments count should match your file

5. **Verify calculations**
   ```
   Expected tokens per comment: ~60 tokens
   Expected cost per 1000 comments: ~$0.006
   ```

### API Test (Programmatic)

```bash
# 1. Check initial state
curl http://localhost:8000/api/metrics/summary | jq

# 2. Process some comments (via upload)

# 3. Check updated metrics
curl http://localhost:8000/api/metrics/summary | jq '.global.total_tokens'

# 4. Get last hour stats
curl http://localhost:8000/api/metrics/recent?hours=1 | jq

# 5. Get task-specific metrics
curl http://localhost:8000/api/metrics/task/{your-task-id} | jq
```

### Integration Test (Full Flow)

```python
# test_dashboard.py
import requests
import time

BASE_URL = "http://localhost:8000"

# 1. Check dashboard is accessible
response = requests.get(f"{BASE_URL}/api/metrics/dashboard")
assert response.status_code == 200
assert "OpenAI Usage Dashboard" in response.text

# 2. Get initial metrics
initial = requests.get(f"{BASE_URL}/api/metrics/summary").json()
print(f"Initial tokens: {initial['global']['total_tokens']}")

# 3. Upload test file (implement your upload logic)
# ...

# 4. Wait for processing
time.sleep(30)

# 5. Get updated metrics
updated = requests.get(f"{BASE_URL}/api/metrics/summary").json()
print(f"Updated tokens: {updated['global']['total_tokens']}")

# 6. Verify increase
assert updated['global']['total_tokens'] > initial['global']['total_tokens']
print("✓ Token tracking working!")
```

---

## Metrics Persistence

### Storage

Metrics are stored in Redis with different TTLs:

| Type | TTL | Key Pattern |
|------|-----|-------------|
| Global metrics | 7 days | `metrics:global` |
| Task metrics | 24 hours | `metrics:task:{task_id}` |
| Hourly metrics | 48 hours | `metrics:hourly:{YYYYMMDDHH}` |
| Daily metrics | 30 days | `metrics:daily:{YYYYMMDD}` |

### Viewing Raw Data

```bash
# Connect to Redis
redis-cli

# Get global metrics
GET metrics:global

# List all task metrics
KEYS metrics:task:*

# Get specific task
GET metrics:task:{task-id}

# Get hourly metrics for current hour
GET metrics:hourly:2025100812
```

---

## Expected Results

### Sample Test (100 comments)

With ultra-minimal prompts:

```
Expected Metrics:
├── Total Tokens: ~6,000 tokens
│   ├── Input Tokens: ~3,600 (60%)
│   └── Output Tokens: ~2,400 (40%)
├── Total Cost: ~$0.0014
├── Comments: 100
├── Avg Tokens/Comment: ~60
└── Processing Time: ~5-10 seconds
```

### Cost Calculations

Based on GPT-4o-mini pricing:

```python
# Input cost
input_tokens = 3600
input_cost = (3600 / 1_000_000) * 0.15 = $0.00054

# Output cost
output_tokens = 2400
output_cost = (2400 / 1_000_000) * 0.60 = $0.00144

# Total
total_cost = $0.00198 (~$0.002)
```

**Per 1000 comments:** ~$0.02
**Per 10,000 comments:** ~$0.20

---

## Troubleshooting

### Issue: Dashboard shows all zeros

**Cause:** No analysis has run yet, or Redis is empty.

**Solution:**
1. Run an analysis (upload a file)
2. Wait for completion
3. Refresh dashboard

### Issue: Metrics not updating

**Cause:** MetricsService not being called, or Redis connection issue.

**Solution:**
1. Check Redis is running: `redis-cli ping`
2. Check API logs for errors
3. Verify OpenAI API calls are being made

### Issue: Cost calculation seems wrong

**Cause:** Pricing constants may be outdated.

**Solution:**
1. Check `MetricsService.PRICE_PER_1M_INPUT_TOKENS`
2. Check `MetricsService.PRICE_PER_1M_OUTPUT_TOKENS`
3. Verify against current OpenAI pricing

### Issue: Dashboard not accessible

**Cause:** Route not registered or API not running.

**Solution:**
1. Verify API is running on port 8000
2. Check main.py includes metrics router
3. Try: `curl http://localhost:8000/api/metrics/summary`

---

## Dashboard Auto-Refresh

The dashboard automatically refreshes every **5 seconds**.

To change the refresh interval, edit `metrics.py`:

```javascript
// Change from 5000ms (5s) to 10000ms (10s)
setInterval(fetchMetrics, 10000);
```

---

## Production Considerations

### Before Deploying

- [ ] Test with real OpenAI API key
- [ ] Verify cost calculations are accurate
- [ ] Test with various file sizes (100, 1000, 5000 rows)
- [ ] Ensure Redis persistence is configured
- [ ] Add authentication to `/api/metrics/reset` endpoint

### Monitoring

Set up alerts for:
- **Daily cost** exceeds threshold
- **Hourly token usage** spikes
- **Average tokens/comment** increases significantly

### Privacy

The dashboard shows aggregate metrics only:
- No customer data exposed
- No comment text visible
- Only token counts and costs

---

## Next Steps

1. **Test with your OpenAI API key**
   - Start services locally
   - Process real customer feedback
   - Monitor actual token usage

2. **Validate cost calculations**
   - Compare dashboard costs with OpenAI billing
   - Verify pricing constants are current

3. **Optional enhancements** (see `local-reports/POLISHING_TASKS.md`)
   - Add charts/graphs
   - Email notifications for cost thresholds
   - Export metrics to CSV

---

## Quick Command Reference

```bash
# Start everything
docker start redis-local && \
cd api && uvicorn app.main:app --reload &
cd api && celery -A app.workers.celery_app worker --loglevel=INFO --pool=solo &
cd web && npm run dev &

# View dashboard
open http://localhost:8000/api/metrics/dashboard

# Get metrics JSON
curl http://localhost:8000/api/metrics/summary | jq

# Reset metrics
curl -X POST http://localhost:8000/api/metrics/reset

# Check Redis
redis-cli GET metrics:global | jq
```

---

## Support

**Issues?**
- Check API logs: Look for "Metrics updated" messages
- Check worker logs: Verify OpenAI calls are being made
- Check Redis: `redis-cli KEYS metrics:*`

**Documentation:**
- Main testing guide: [LOCAL_TESTING_GUIDE.md](./LOCAL_TESTING_GUIDE.md)
- Polishing tasks: [local-reports/POLISHING_TASKS.md](./local-reports/POLISHING_TASKS.md)

---

**Status:** ✅ Ready to test with real OpenAI API key!

Enjoy your new real-time token monitoring dashboard! 🚀
