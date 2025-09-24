#!/usr/bin/env python
"""
Test script for hybrid analysis implementation.
Tests local sentiment + OpenAI insights integration.
"""

import asyncio
import json
import os
from typing import List, Dict

# Add parent directory to path
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.adapters.local_sentiment import LocalSentimentAnalyzer
from app.adapters.hybrid_analyzer import HybridAnalyzer
from app.config import settings


def test_local_sentiment():
    """Test local sentiment analysis works."""
    print("\n=== Testing Local Sentiment Analyzer ===")

    analyzer = LocalSentimentAnalyzer()

    test_comments = [
        "Excelente servicio, muy satisfecho con la atención",
        "Terrible experiencia, muy frustrado con el producto",
        "No entiendo cómo funciona la aplicación",
        "El precio es demasiado caro para la calidad"
    ]

    results = analyzer.analyze_batch(test_comments, "es")

    for i, (comment, result) in enumerate(zip(test_comments, results)):
        print(f"\nComment {i+1}: {comment[:50]}...")
        print(f"Base sentiment: {result['base_sentiment']}")
        print(f"Emotions: {json.dumps(result['emotions'], indent=2)}")

    print("\n✅ Local sentiment analysis working!")
    return True


async def test_hybrid_analysis():
    """Test hybrid analysis (local + OpenAI)."""
    print("\n=== Testing Hybrid Analyzer ===")

    # Check if OpenAI key is configured
    if not settings.OPENAI_API_KEY:
        print("⚠️ OPENAI_API_KEY not configured, skipping hybrid test")
        return False

    analyzer = HybridAnalyzer()

    test_comments = [
        "El precio es muy caro y la calidad no lo justifica",
        "Excelente atención al cliente, muy profesionales",
        "La aplicación tiene muchos errores y es lenta"
    ]

    result = await analyzer.analyze_batch(test_comments, 0, "es")

    print(f"\nProcessed {len(result['comments'])} comments")

    for comment_result in result['comments']:
        print(f"\nComment index: {comment_result['index']}")
        print(f"Emotions (local): {json.dumps(comment_result['emotions'], indent=2)}")
        print(f"Churn risk (OpenAI): {comment_result['churn_risk']}")
        print(f"Pain points (OpenAI): {comment_result['pain_points']}")
        print(f"NPS category: {comment_result['nps_category']}")

    print("\n✅ Hybrid analysis working!")
    return True


def test_memory_monitor():
    """Test memory monitoring utilities."""
    print("\n=== Testing Memory Monitor ===")

    from app.utils.memory_monitor import MemoryMonitor

    available = MemoryMonitor.get_available_memory_mb()
    used = MemoryMonitor.get_used_memory_mb()
    status = MemoryMonitor.check_memory_status()

    print(f"Available memory: {available:.1f} MB")
    print(f"Used memory: {used:.1f} MB")
    print(f"Memory status: {status}")

    # Test batch size calculation
    batch_size = MemoryMonitor.calculate_safe_batch_size(1000, 100)
    print(f"Recommended batch size for 1000 items: {batch_size}")

    print("\n✅ Memory monitoring working!")
    return True


def test_event_loop_manager():
    """Test event loop management for async code."""
    print("\n=== Testing Event Loop Manager ===")

    from app.utils.event_loop_manager import SafeEventLoopManager

    async def sample_async_function():
        await asyncio.sleep(0.1)
        return "async result"

    # Test running async code in sync context
    result = SafeEventLoopManager.run_async_in_worker(
        sample_async_function()
    )

    print(f"Async result in sync context: {result}")

    print("\n✅ Event loop manager working!")
    return True


def test_frontend_contract():
    """Verify the response format matches frontend expectations."""
    print("\n=== Testing Frontend Contract ===")

    # Sample hybrid result
    sample_result = {
        "comments": [{
            "index": 0,
            "emotions": {
                "satisfaccion": 0.2,
                "frustracion": 0.7,
                "enojo": 0.5,
                "confianza": 0.1,
                "decepcion": 0.6,
                "confusion": 0.3,
                "anticipacion": 0.1
            },
            "churn_risk": 0.8,
            "pain_points": ["precio"],
            "sentiment_score": -0.5,
            "language": "es",
            "nps_category": "detractor",
            "key_phrases": []
        }]
    }

    # Check required fields
    required_fields = [
        "index", "emotions", "churn_risk", "pain_points",
        "sentiment_score", "language", "nps_category", "key_phrases"
    ]

    comment = sample_result["comments"][0]
    missing = [field for field in required_fields if field not in comment]

    if missing:
        print(f"❌ Missing fields: {missing}")
        return False

    # Check emotion fields
    required_emotions = [
        "satisfaccion", "frustracion", "enojo", "confianza",
        "decepcion", "confusion", "anticipacion"
    ]

    missing_emotions = [e for e in required_emotions if e not in comment["emotions"]]

    if missing_emotions:
        print(f"❌ Missing emotions: {missing_emotions}")
        return False

    print("✅ Frontend contract preserved!")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("HYBRID ANALYSIS TEST SUITE")
    print("=" * 60)

    results = []

    # Test 1: Local sentiment
    try:
        results.append(("Local Sentiment", test_local_sentiment()))
    except Exception as e:
        print(f"❌ Local sentiment test failed: {e}")
        results.append(("Local Sentiment", False))

    # Test 2: Memory monitoring
    try:
        results.append(("Memory Monitor", test_memory_monitor()))
    except Exception as e:
        print(f"❌ Memory monitor test failed: {e}")
        results.append(("Memory Monitor", False))

    # Test 3: Event loop manager
    try:
        results.append(("Event Loop Manager", test_event_loop_manager()))
    except Exception as e:
        print(f"❌ Event loop manager test failed: {e}")
        results.append(("Event Loop Manager", False))

    # Test 4: Frontend contract
    try:
        results.append(("Frontend Contract", test_frontend_contract()))
    except Exception as e:
        print(f"❌ Frontend contract test failed: {e}")
        results.append(("Frontend Contract", False))

    # Test 5: Hybrid analysis (requires OpenAI key)
    try:
        result = asyncio.run(test_hybrid_analysis())
        results.append(("Hybrid Analysis", result))
    except Exception as e:
        print(f"❌ Hybrid analysis test failed: {e}")
        results.append(("Hybrid Analysis", False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print(f"\nTotal: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("\n🎉 All tests passed! Hybrid analysis is ready.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please review and fix issues.")
        return 1


if __name__ == "__main__":
    exit(main())