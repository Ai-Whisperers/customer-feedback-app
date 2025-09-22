# Pipeline Optimization Savepoint - December 21, 2024

## Current State (Commit: 09a8b65)

### Completed Improvements
✅ **Modular NPS Calculator** with shifted default (0-100 scale, no negatives)
✅ **Flexible File Parser** with dynamic column detection
✅ **Integration complete** without breaking existing pipeline
✅ **Environment variables** configured with sensible defaults

### Current Pipeline Performance
- **850 rows**: ~8-10 seconds
- **1800 rows**: ~18-20 seconds
- **3000 rows**: ~30-35 seconds
- **Bottleneck**: Sequential OpenAI API calls (2-3s per batch)

### Current Architecture Flow
```
1. upload.py → Validates file using file_parser.py
2. Redis stores file content (base64 encoded)
3. Celery worker picks up task
4. analysis_service.py loads and normalizes data
5. OpenAI analyzer processes in batches (50-100 rows)
6. Results aggregated and stored in Redis
7. Frontend polls for results
```

## Target Performance Goals
- **850 rows**: < 5 seconds
- **1800 rows**: < 10 seconds
- **3000 rows**: < 15 seconds

## Implementation Plan for Parallel Processing

### Phase 1: Async Infrastructure (Priority: HIGH)

#### 1.1 Update OpenAI Analyzer (`api/app/adapters/openai/analyzer.py`)
**Current State**: Synchronous requests using `requests` library
**Target State**: Async requests using `aiohttp`

```python
# Key changes needed:
- Replace requests with aiohttp
- Convert analyze_batch() to async def analyze_batch()
- Implement semaphore for rate limiting (8 RPS)
- Add concurrent batch processing with asyncio.gather()
```

**Files to modify**:
- `api/app/adapters/openai/analyzer.py` (lines ~50-150)
- `api/app/adapters/openai/__init__.py`

#### 1.2 Update Celery Worker (`api/app/workers/tasks.py`)
**Current State**: Synchronous task processing
**Target State**: Async-aware task with event loop

```python
# Key changes needed:
- Add async event loop in analyze_feedback task
- Implement concurrent batch processing
- Maintain progress updates during parallel execution
```

**Files to modify**:
- `api/app/workers/tasks.py` (lines ~100-200)

### Phase 2: Optimization Parameters (Priority: HIGH)

#### 2.1 Increase Batch Size
**Current**: 50-100 rows per batch
**Target**: 100-150 rows per batch

**Files to modify**:
- `api/app/config.py` - Update MAX_BATCH_SIZE
- `api/.env.example` - Document new defaults

#### 2.2 Configure Concurrency
**New Environment Variables**:
```env
OPENAI_CONCURRENT_WORKERS=4  # Number of parallel API calls
OPENAI_RATE_LIMIT_RPS=8      # Requests per second limit
BATCH_SIZE_OPTIMAL=120        # Optimal batch size for token limits
```

### Phase 3: Caching Layer (Priority: MEDIUM)

#### 3.1 Implement Comment Deduplication Cache
**Strategy**: Hash-based caching for similar comments

```python
# Implementation approach:
- Generate hash for normalized comment text
- Check Redis cache before API call
- Store results with 7-day TTL
- Skip API calls for cached comments
```

**Files to create**:
- `api/app/core/cache_manager.py`

**Files to modify**:
- `api/app/adapters/openai/analyzer.py`
- `api/app/workers/tasks.py`

### Phase 4: Progress Tracking (Priority: LOW)

#### 4.1 Enhanced Progress Updates
**Current**: Linear progress updates
**Target**: Parallel-aware progress tracking

**Files to modify**:
- `api/app/services/status_service.py`

## Implementation Checklist

### Prerequisites
- [ ] Backup current working state
- [ ] Create feature branch: `feat/parallel-processing-optimization`
- [ ] Review OpenAI API rate limits documentation
- [ ] Test current baseline performance with timer

### Core Implementation
- [ ] Install aiohttp: `pip install aiohttp`
- [ ] Convert analyzer.py to async/await pattern
- [ ] Implement semaphore-based rate limiting
- [ ] Update Celery worker for async execution
- [ ] Add concurrent batch processing logic
- [ ] Update progress tracking for parallel execution
- [ ] Increase batch size to 120
- [ ] Add concurrency environment variables
- [ ] Implement basic comment caching
- [ ] Add cache hit/miss metrics

### Testing
- [ ] Unit tests for async analyzer
- [ ] Integration test with 850-row file
- [ ] Performance test with 1800-row file
- [ ] Stress test with 3000-row file
- [ ] Verify Redis memory usage
- [ ] Check OpenAI API rate limit compliance
- [ ] Test error handling in parallel execution
- [ ] Verify progress updates accuracy

### Documentation
- [ ] Update API documentation
- [ ] Document new environment variables
- [ ] Add performance benchmarks
- [ ] Update deployment guide

## Code Snippets for Implementation

### 1. Async Analyzer Structure
```python
# api/app/adapters/openai/analyzer.py

import asyncio
import aiohttp
from typing import List, Dict, Any

class OpenAIAnalyzer:
    def __init__(self):
        self.semaphore = asyncio.Semaphore(8)  # Rate limit: 8 RPS
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args):
        await self.session.close()

    async def analyze_batch(self, comments: List[str]) -> List[Dict[str, Any]]:
        async with self.semaphore:
            async with self.session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=self._build_request(comments)
            ) as response:
                result = await response.json()
                return self._parse_response(result)

    async def analyze_all_batches(self, batches: List[List[str]]) -> List[Dict[str, Any]]:
        tasks = [self.analyze_batch(batch) for batch in batches]
        results = await asyncio.gather(*tasks)
        return [item for batch_result in results for item in batch_result]
```

### 2. Updated Celery Worker
```python
# api/app/workers/tasks.py

import asyncio
from app.adapters.openai import OpenAIAnalyzer

@celery_app.task(bind=True)
def analyze_feedback(self, task_id: str, file_info: Dict[str, Any]) -> str:
    # ... existing setup code ...

    # Create event loop for async execution
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Run async analysis
        results = loop.run_until_complete(
            run_parallel_analysis(batches, task_id)
        )
    finally:
        loop.close()

    return results

async def run_parallel_analysis(batches, task_id):
    async with OpenAIAnalyzer() as analyzer:
        results = await analyzer.analyze_all_batches(batches)
        # Update progress periodically
        return results
```

### 3. Cache Implementation
```python
# api/app/core/cache_manager.py

import hashlib
import json
from typing import Optional, Dict, Any

class CommentCache:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.ttl = 7 * 24 * 3600  # 7 days

    def get_cache_key(self, comment: str) -> str:
        normalized = comment.lower().strip()
        return f"analysis:cache:{hashlib.md5(normalized.encode()).hexdigest()}"

    def get(self, comment: str) -> Optional[Dict[str, Any]]:
        key = self.get_cache_key(comment)
        cached = self.redis.get(key)
        return json.loads(cached) if cached else None

    def set(self, comment: str, analysis: Dict[str, Any]):
        key = self.get_cache_key(comment)
        self.redis.setex(key, self.ttl, json.dumps(analysis))

    def get_many(self, comments: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        # Batch get from Redis
        keys = [self.get_cache_key(c) for c in comments]
        values = self.redis.mget(keys)
        return {
            comment: json.loads(val) if val else None
            for comment, val in zip(comments, values)
        }
```

## Performance Expectations

### Before Optimization
| Rows | Current Time | API Calls | Cost |
|------|-------------|-----------|------|
| 850  | 8-10s       | 17        | $0.02 |
| 1800 | 18-20s      | 36        | $0.04 |
| 3000 | 30-35s      | 60        | $0.07 |

### After Optimization
| Rows | Target Time | API Calls | Cost (with cache) |
|------|------------|-----------|------------------|
| 850  | < 5s       | 6-8       | $0.01 |
| 1800 | < 10s      | 12-15     | $0.02 |
| 3000 | < 15s      | 20-25     | $0.03 |

## Risk Mitigation

1. **Rate Limiting**: Implement exponential backoff for 429 errors
2. **Memory Usage**: Monitor Redis memory with large concurrent batches
3. **Error Handling**: Implement retry logic for failed batches
4. **Rollback Plan**: Keep synchronous code path as fallback

## Environment Variables Summary

### Existing (Keep as-is)
```env
OPENAI_API_KEY=your-key
AI_MODEL=gpt-4o-mini
MAX_RPS=8
MAX_BATCH_SIZE=50
NPS_CALCULATION_METHOD=shifted
FILE_PARSER_MODE=base
```

### New (To be added)
```env
# Parallel Processing
OPENAI_CONCURRENT_WORKERS=4
BATCH_SIZE_OPTIMAL=120
ENABLE_PARALLEL_PROCESSING=true
ENABLE_COMMENT_CACHE=true
CACHE_TTL_DAYS=7

# Performance Monitoring
LOG_PERFORMANCE_METRICS=true
ALERT_THRESHOLD_SECONDS=15
```

## Testing Data

### Test Files Location
- `test/fixtures/test_850_rows.xlsx`
- `test/fixtures/test_1800_rows.xlsx`
- `test/fixtures/test_3000_rows.xlsx`

### Performance Benchmark Script
```bash
# Create benchmark script
python api/scripts/benchmark_pipeline.py --file test_850_rows.xlsx --iterations 5
```

## Next Steps

1. **Create feature branch** and implement async analyzer
2. **Test with small file** (100 rows) to verify correctness
3. **Gradually increase** concurrency and batch size
4. **Monitor API rate limits** and adjust semaphore
5. **Implement caching** after parallel processing works
6. **Run full benchmark** suite
7. **Document performance** improvements
8. **Deploy to staging** for real-world testing

## Notes

- Current commit hash: `09a8b65`
- All file paths relative to project root
- Budget constraint: $5 for MVP testing
- Target: < 10 seconds for 1800 rows
- Maintain backward compatibility
- No breaking changes to API contract

---

**Created**: December 21, 2024
**Author**: Pipeline Optimization Team
**Status**: Ready for Implementation
**Priority**: HIGH - Core performance improvement for MVP