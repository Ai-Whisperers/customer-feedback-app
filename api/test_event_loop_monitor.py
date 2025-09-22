"""
Test script for event loop monitoring functionality.
"""

import os
import sys
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

sys.path.append('.')

from app.utils.event_loop_monitor import (
    monitor_event_loop,
    log_loop_state,
    check_loop_conflict,
    get_loop_summary,
    enable_monitoring
)


@monitor_event_loop("test_sync_function")
def sync_function():
    """Test sync function with monitoring."""
    log_loop_state("Inside sync function")
    return "sync_result"


@monitor_event_loop("test_async_function")
async def async_function():
    """Test async function with monitoring."""
    log_loop_state("Inside async function")
    await asyncio.sleep(0.1)
    return "async_result"


def test_basic_monitoring():
    """Test basic monitoring functionality."""
    print("\n" + "=" * 60)
    print("Testing Basic Monitoring")
    print("=" * 60)

    # Enable monitoring
    enable_monitoring(True)

    # Test sync function
    print("\nTesting sync function:")
    result = sync_function()
    print(f"Result: {result}")

    # Test async function
    print("\nTesting async function:")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(async_function())
    loop.close()
    print(f"Result: {result}")

    # Get summary
    summary = get_loop_summary()
    print("\nMonitoring Summary:")
    print(f"Current thread: {summary['current_state']['thread_name']}")
    print(f"Loop exists: {summary['current_state']['loop_exists']}")
    print(f"History checks: {summary['history']['total_checks']}")

    print("\n✓ Basic monitoring test passed")


def test_loop_conflict_detection():
    """Test event loop conflict detection."""
    print("\n" + "=" * 60)
    print("Testing Loop Conflict Detection")
    print("=" * 60)

    # Scenario 1: No loop exists
    print("\nScenario 1: No loop in thread")
    conflict = check_loop_conflict()
    if conflict:
        print(f"Conflict detected: {conflict['conflict_type']}")
        print(f"Recommendation: {conflict['recommendation']}")
    else:
        print("No conflict detected")

    # Scenario 2: Create and run a loop
    print("\nScenario 2: Running loop")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def check_during_run():
        log_loop_state("Inside running loop")
        conflict = check_loop_conflict()
        if conflict:
            print(f"Conflict detected: {conflict['conflict_type']}")
            print(f"Recommendation: {conflict['recommendation']}")
        return conflict

    conflict = loop.run_until_complete(check_during_run())
    loop.close()

    print("\n✓ Conflict detection test passed")


def test_multithreading():
    """Test monitoring across threads."""
    print("\n" + "=" * 60)
    print("Testing Multithreading Monitoring")
    print("=" * 60)

    def thread_function(thread_id):
        """Function to run in thread."""
        log_loop_state(f"Thread {thread_id} starting")

        # Try to get/create loop
        try:
            loop = asyncio.get_event_loop()
            log_loop_state(f"Thread {thread_id} got loop", loop_id=id(loop))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            log_loop_state(f"Thread {thread_id} created new loop", loop_id=id(loop))

        # Run something async
        async def thread_async_work():
            await asyncio.sleep(0.01)
            return f"Thread {thread_id} completed"

        result = loop.run_until_complete(thread_async_work())
        loop.close()

        log_loop_state(f"Thread {thread_id} finished")
        return result

    # Run in multiple threads
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(thread_function, i) for i in range(3)]
        results = [f.result() for f in futures]

    print(f"\nThread results: {results}")

    # Get summary after threading
    summary = get_loop_summary()
    print(f"\nUnique threads seen: {summary['history']['unique_threads']}")
    print(f"Unique loops created: {summary['history']['unique_loop_ids']}")

    print("\n✓ Multithreading test passed")


def test_celery_simulation():
    """Simulate Celery-like behavior."""
    print("\n" + "=" * 60)
    print("Testing Celery-like Simulation")
    print("=" * 60)

    @monitor_event_loop("simulated_celery_task")
    def celery_task():
        """Simulate a Celery task."""
        log_loop_state("Celery task starting")

        # Celery might already have a loop
        try:
            existing_loop = asyncio.get_event_loop()
            log_loop_state("Found existing loop in Celery",
                          loop_id=id(existing_loop),
                          is_running=existing_loop.is_running())
        except RuntimeError:
            pass

        # Create new loop (like our analyze_batch does)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        log_loop_state("Created new loop for task", loop_id=id(loop))

        # Try to run something
        async def async_work():
            return "celery_work_done"

        try:
            result = loop.run_until_complete(async_work())
            log_loop_state("Task completed successfully")
            return result
        finally:
            loop.close()
            log_loop_state("Task loop closed")

    # Run the simulated task
    result = celery_task()
    print(f"\nCelery task result: {result}")

    print("\n✓ Celery simulation test passed")


def test_error_handling():
    """Test that monitoring doesn't break on errors."""
    print("\n" + "=" * 60)
    print("Testing Error Handling")
    print("=" * 60)

    @monitor_event_loop("error_prone_function")
    def function_with_error():
        """Function that raises an error."""
        log_loop_state("About to raise error")
        raise ValueError("Test error")

    # Test that monitoring doesn't prevent error propagation
    try:
        function_with_error()
        print("✗ Error was not raised!")
    except ValueError as e:
        print(f"✓ Error properly propagated: {e}")

    # Check that monitoring continued
    summary = get_loop_summary()
    print(f"Monitoring still active: {summary['monitoring_enabled']}")

    print("\n✓ Error handling test passed")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Event Loop Monitor Test Suite")
    print("=" * 60)

    tests = [
        ("Basic Monitoring", test_basic_monitoring),
        ("Conflict Detection", test_loop_conflict_detection),
        ("Multithreading", test_multithreading),
        ("Celery Simulation", test_celery_simulation),
        ("Error Handling", test_error_handling)
    ]

    results = []
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, True))
        except Exception as e:
            print(f"\n✗ {name} test failed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{name:25} {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    # Final monitoring summary
    final_summary = get_loop_summary()
    print(f"\nTotal monitoring events: {final_summary['history']['total_checks']}")

    if passed == total:
        print("\n🎉 All tests passed! Event loop monitoring is working correctly.")
    else:
        print(f"\n⚠ {total - passed} test(s) failed.")


if __name__ == "__main__":
    main()