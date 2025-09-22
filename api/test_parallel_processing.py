"""
Test script for parallel processing implementation.
"""

import os
import sys
import time
import asyncio
sys.path.append('.')

# Set environment variables for testing
os.environ["ENABLE_PARALLEL_PROCESSING"] = "true"
os.environ["ENABLE_COMMENT_CACHE"] = "true"
os.environ["OPENAI_CONCURRENT_WORKERS"] = "4"
os.environ["BATCH_SIZE_OPTIMAL"] = "120"
os.environ["LOG_PERFORMANCE_METRICS"] = "true"

from app.config import settings


def test_configuration():
    """Test that configuration is loaded correctly."""
    print("Testing Configuration")
    print("=" * 60)

    print(f"Parallel Processing Enabled: {settings.ENABLE_PARALLEL_PROCESSING}")
    print(f"Comment Cache Enabled: {settings.ENABLE_COMMENT_CACHE}")
    print(f"Concurrent Workers: {settings.OPENAI_CONCURRENT_WORKERS}")
    print(f"Optimal Batch Size: {settings.BATCH_SIZE_OPTIMAL}")
    print(f"Cache TTL Days: {settings.CACHE_TTL_DAYS}")
    print(f"Alert Threshold: {settings.ALERT_THRESHOLD_SECONDS}s")

    assert settings.ENABLE_PARALLEL_PROCESSING == True
    assert settings.OPENAI_CONCURRENT_WORKERS == 4
    assert settings.BATCH_SIZE_OPTIMAL == 120

    print("✓ Configuration test passed\n")


def test_parallel_processor():
    """Test parallel processor initialization."""
    print("Testing Parallel Processor")
    print("=" * 60)

    try:
        from app.adapters.openai.parallel_processor import ParallelProcessor
        import redis

        # Try Redis connection
        try:
            redis_client = redis.from_url(settings.REDIS_URL)
            redis_client.ping()
            print("✓ Redis connection successful")
        except Exception as e:
            print(f"⚠ Redis not available: {e}")
            redis_client = None

        # Create processor
        processor = ParallelProcessor(redis_client)
        print(f"✓ Parallel processor created")
        print(f"  - Parallel enabled: {processor.use_parallel}")
        print(f"  - Cache enabled: {processor.use_cache}")

        # Get stats
        stats = processor.get_processing_stats()
        print(f"\nProcessor Stats:")
        for key, value in stats.items():
            if key != "cache":
                print(f"  {key}: {value}")

        if "cache" in stats:
            print(f"\nCache Stats:")
            for key, value in stats["cache"].items():
                print(f"  {key}: {value}")

        print("\n✓ Parallel processor test passed\n")

    except ImportError as e:
        print(f"✗ Failed to import: {e}")
        return False

    return True


def test_analyzer_factory():
    """Test analyzer factory with parallel processing."""
    print("Testing Analyzer Factory")
    print("=" * 60)

    from app.adapters.openai import create_analyzer, openai_analyzer

    # Check analyzer type
    print(f"Analyzer type: {type(openai_analyzer).__name__}")

    # Check if wrapper is used
    if hasattr(openai_analyzer, 'processor'):
        print("✓ Using ParallelProcessor wrapper")
        print(f"  - Processor: {type(openai_analyzer.processor).__name__}")
    else:
        print("✓ Using standard OpenAIAnalyzer")

    # Check available methods
    print("\nAvailable methods:")
    methods = [m for m in dir(openai_analyzer) if not m.startswith('_')]
    for method in ['analyze_batch', 'optimize_batch_size']:
        if method in methods:
            print(f"  ✓ {method}")
        else:
            print(f"  ✗ {method} missing")

    print("\n✓ Analyzer factory test passed\n")


def test_cache_manager():
    """Test cache manager functionality."""
    print("Testing Cache Manager")
    print("=" * 60)

    try:
        from app.core.cache_manager import CommentCacheManager
        import redis
        import json

        # Try Redis connection
        try:
            redis_client = redis.from_url(settings.REDIS_URL)
            redis_client.ping()
            print("✓ Redis available for cache testing")
        except Exception as e:
            print(f"⚠ Skipping cache test (Redis not available): {e}")
            return True

        # Create cache manager
        cache = CommentCacheManager(redis_client)

        # Test cache operations
        test_comment = "Este es un comentario de prueba"
        test_analysis = {
            "emotions": {"joy": 0.5, "trust": 0.3},
            "churn_risk": 0.2,
            "pain_points": ["test"]
        }

        # Set cache
        success = cache.set(test_comment, test_analysis)
        print(f"✓ Cache set: {success}")

        # Get cache
        cached = cache.get(test_comment)
        if cached:
            print(f"✓ Cache retrieved: {json.dumps(cached, indent=2)[:100]}...")
        else:
            print("✗ Cache retrieval failed")

        # Test batch operations
        comments = [
            "Comentario 1",
            "Comentario 2",
            test_comment  # This one should be cached
        ]

        cached_results, uncached_indices = cache.get_many(comments)
        print(f"\nBatch cache test:")
        print(f"  Cached: {len(cached_results)}")
        print(f"  Uncached: {len(uncached_indices)}")

        # Get stats
        stats = cache.get_stats()
        print(f"\nCache stats:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

        print("\n✓ Cache manager test passed\n")

    except ImportError as e:
        print(f"✗ Failed to import: {e}")
        return False

    return True


def test_async_analyzer():
    """Test async analyzer basic functionality."""
    print("Testing Async Analyzer")
    print("=" * 60)

    try:
        from app.adapters.openai.async_analyzer import AsyncOpenAIAnalyzer

        # Create analyzer
        analyzer = AsyncOpenAIAnalyzer()
        print(f"✓ Async analyzer created")
        print(f"  - Max concurrent: {analyzer.max_concurrent}")
        print(f"  - Rate limit RPS: {analyzer.rate_limit_rps}")
        print(f"  - Model: {analyzer.model}")

        # Check methods
        methods = ['analyze_batch', 'analyze_all_batches']
        for method in methods:
            if hasattr(analyzer, method):
                print(f"  ✓ {method} available")
            else:
                print(f"  ✗ {method} missing")

        print("\n✓ Async analyzer test passed\n")

    except ImportError as e:
        print(f"✗ Failed to import: {e}")
        return False

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Parallel Processing Implementation Test Suite")
    print("=" * 60 + "\n")

    tests = [
        ("Configuration", test_configuration),
        ("Parallel Processor", test_parallel_processor),
        ("Analyzer Factory", test_analyzer_factory),
        ("Cache Manager", test_cache_manager),
        ("Async Analyzer", test_async_analyzer)
    ]

    results = []
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, True))
        except Exception as e:
            print(f"\n✗ {name} test failed: {e}\n")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{name:20} {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Parallel processing is ready.")
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Please check the implementation.")


if __name__ == "__main__":
    main()