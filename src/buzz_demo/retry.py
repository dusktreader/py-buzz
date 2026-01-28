"""
This example set demonstrates the use of the `retry()` decorator.
This decorator retries a function with exponential backoff when it raises
specified exceptions.
"""

from __future__ import annotations

import asyncio

from buzz import Buzz


def demo_1__simple():
    """
    This function demonstrates basic retry functionality. The decorated function
    will be retried up to 3 times if it raises an exception.
    """
    attempt_count = 0

    @Buzz.retry("Operation failed after {attempts} attempts", max_attempts=3, backoff=0.5, jitter=False)
    def flaky_operation():
        nonlocal attempt_count
        attempt_count += 1
        print(f"Attempt {attempt_count}...")

        if attempt_count < 3:
            raise ConnectionError(f"Connection failed on attempt {attempt_count}")

        return "Success!"

    result = flaky_operation()
    print(f"Operation completed: {result}")


def demo_2__selective_retry():
    """
    This function demonstrates retrying only specific exception types.
    The `retry_on` parameter specifies which exceptions should trigger a retry.
    Other exceptions will be raised immediately without retry.
    """
    attempt_count = 0

    @Buzz.retry(
        "Network operation failed after {attempts} attempts",
        max_attempts=3,
        backoff=0.5,
        jitter=False,
        retry_on=(ConnectionError, TimeoutError),
    )
    def network_operation():
        nonlocal attempt_count
        attempt_count += 1
        print(f"Attempt {attempt_count}...")

        if attempt_count == 1:
            # This will be retried
            raise ConnectionError("Network unreachable")
        elif attempt_count == 2:
            # This will also be retried
            raise TimeoutError("Request timed out")

        return "Data retrieved successfully"

    result = network_operation()
    print(f"Result: {result}")


def demo_3__with_callback():
    """
    This function demonstrates using a callback to monitor retry attempts.
    The `on_retry` callback is invoked before each retry attempt.
    """

    @Buzz.retry(
        "Service call failed after {attempts} attempts",
        max_attempts=4,
        backoff=0.5,
        jitter=False,
        on_retry=lambda attempt, exc: print(f"  → Retry attempt {attempt} after error: {exc}"),
    )
    def unreliable_service():
        import random

        if random.random() < 0.7:  # 70% chance of failure
            raise ConnectionError("Service temporarily unavailable")

        return "Service response"

    try:
        result = unreliable_service()
        print(f"Got result: {result}")
    except Buzz as e:
        print(f"All retries exhausted: {e}")


def demo_4__exponential_backoff():
    """
    This function demonstrates exponential backoff behavior.
    The delay between retries increases exponentially: backoff^attempt.
    """
    import time

    attempt_times = []

    @Buzz.retry("Operation failed after {attempts} attempts", max_attempts=4, backoff=2.0, jitter=False)
    def slow_failing_operation():
        attempt_times.append(time.time())
        print(f"Attempt {len(attempt_times)} at {time.strftime('%H:%M:%S')}")
        raise ConnectionError("Still failing")

    try:
        slow_failing_operation()
    except Buzz:
        print("\nDelay analysis:")
        print("  Delays between attempts (exponential backoff with base 2.0):")
        for i in range(1, len(attempt_times)):
            delay = attempt_times[i] - attempt_times[i - 1]
            print(f"    Attempt {i} → {i + 1}: {delay:.2f}s")


def demo_5__async_retry():
    """
    This function demonstrates async retry functionality.
    The `retry_async()` decorator works with async functions and uses
    `asyncio.sleep()` for delays.
    """
    attempt_count = 0

    @Buzz.retry_async("Async operation failed after {attempts} attempts", max_attempts=3, backoff=0.5, jitter=False)
    async def async_api_call():
        nonlocal attempt_count
        attempt_count += 1
        print(f"Async attempt {attempt_count}...")

        if attempt_count < 3:
            raise ConnectionError(f"API not responding (attempt {attempt_count})")

        return {"status": "ok", "data": "response"}

    async def run_async_demo():
        result = await async_api_call()
        print(f"API response: {result}")

    asyncio.run(run_async_demo())


def demo_6__custom_message():
    """
    This function demonstrates custom error messages on final failure.
    The message can include the {attempts} placeholder.
    """

    @Buzz.retry(
        "Failed to connect after {attempts} attempts",
        max_attempts=3,
        backoff=0.5,
        jitter=False,
    )
    def always_fails():
        print("Attempting connection...")
        raise ConnectionError("Connection refused")

    try:
        always_fails()
    except Buzz as e:
        print(f"Final error: {e}")
