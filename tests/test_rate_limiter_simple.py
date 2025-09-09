"""
Simple test suite for rate limiting system.
Tests RateLimiter functionality without pytest dependencies.
"""
import os
import sys
import time
from datetime import datetime, timedelta

# Add src to path for imports
test_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(test_dir)
src_path = os.path.join(project_root, 'src')

if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from utils.rate_limiter import CallRecord, RateLimiter, RateLimitStatus
    print("✅ Rate limiter imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


def test_rate_limiter_initialization():
    """Test rate limiter initialization with default and custom settings"""
    print("Testing rate limiter initialization...")

    # Test default initialization
    limiter = RateLimiter()
    assert limiter.calls_per_hour == 100
    assert limiter.window_seconds == 3600  # 1 hour
    assert len(limiter.call_history) == 0
    assert limiter.total_calls == 0

    # Test custom initialization
    custom_limiter = RateLimiter(calls_per_hour=50, window_hours=0.5)
    assert custom_limiter.calls_per_hour == 50
    assert custom_limiter.window_seconds == 1800  # 0.5 hours = 1800 seconds

    print("✅ Rate limiter initialization test passed")


def test_can_make_call_basic():
    """Test basic can_make_call functionality"""
    print("Testing basic can_make_call functionality...")

    limiter = RateLimiter(calls_per_hour=5)  # Small limit for testing

    # Should be able to make calls initially
    assert limiter.can_make_call() == True

    # Record some calls
    for i in range(4):
        limiter.record_call(success=True)
        assert limiter.can_make_call() == True

    # Record the 5th call (at limit)
    limiter.record_call(success=True)
    assert limiter.can_make_call() == False  # Should be at limit

    print("✅ Basic can_make_call test passed")


def test_call_recording():
    """Test call recording functionality"""
    print("Testing call recording...")

    limiter = RateLimiter()
    limiter.reset_all_tracking()

    # Record successful call
    limiter.record_call(success=True)
    assert limiter.total_calls == 1
    assert limiter.successful_calls == 1
    assert limiter.failed_calls == 0
    assert len(limiter.call_history) == 1

    # Record failed call
    limiter.record_call(success=False, error_message="API Error")
    assert limiter.total_calls == 2
    assert limiter.successful_calls == 1
    assert limiter.failed_calls == 1
    assert len(limiter.call_history) == 2

    # Check call record details
    failed_call = limiter.call_history[-1]
    assert failed_call.success == False
    assert failed_call.error_message == "API Error"
    assert failed_call.timestamp > 0

    print("✅ Call recording test passed")


def test_rate_limit_status():
    """Test rate limit status information"""
    print("Testing rate limit status...")

    limiter = RateLimiter(calls_per_hour=10)
    limiter.reset_all_tracking()

    # Test initial status
    status = limiter.get_rate_limit_status()
    assert status.calls_made == 0
    assert status.calls_remaining == 10
    assert status.limit_exceeded == False

    # Record some calls
    for i in range(7):
        limiter.record_call(success=True)

    status = limiter.get_rate_limit_status()
    assert status.calls_made == 7
    assert status.calls_remaining == 3
    assert status.limit_exceeded == False

    # Exceed the limit
    for i in range(4):  # 7 + 4 = 11 > 10
        limiter.record_call(success=True)

    status = limiter.get_rate_limit_status()
    assert status.calls_made == 11
    assert status.calls_remaining == 0
    assert status.limit_exceeded == True

    print("✅ Rate limit status test passed")


def test_time_calculations():
    """Test time-based calculations"""
    print("Testing time calculations...")

    limiter = RateLimiter(calls_per_hour=5)
    limiter.reset_all_tracking()

    # Fill up the rate limit
    for i in range(5):
        limiter.record_call(success=True)

    # Should not be able to make more calls
    assert limiter.can_make_call() == False

    # Time until next call should be positive
    time_until_next = limiter.get_time_until_next_call()
    assert time_until_next > timedelta(0)
    assert time_until_next <= timedelta(hours=1)

    # Status should show reset time in the future
    status = limiter.get_rate_limit_status()
    assert status.reset_time > datetime.now()
    assert status.time_until_reset > timedelta(0)

    print("✅ Time calculations test passed")


def test_statistics():
    """Test statistics gathering"""
    print("Testing statistics...")

    limiter = RateLimiter(calls_per_hour=10)
    limiter.reset_all_tracking()

    # Record mixed success/failure calls
    for i in range(7):
        limiter.record_call(success=True)
    for i in range(2):
        limiter.record_call(success=False, error_message="Test error")

    stats = limiter.get_statistics()

    assert stats["calls_per_hour_limit"] == 10
    assert stats["total_calls_ever"] == 9
    assert stats["successful_calls_ever"] == 7
    assert stats["failed_calls_ever"] == 2
    assert stats["calls_in_current_window"] == 9
    assert stats["successful_in_window"] == 7
    assert stats["failed_in_window"] == 2
    assert stats["success_rate_percent"] == 77.78  # 7/9 * 100
    assert stats["can_make_call_now"] == True

    print("✅ Statistics test passed")


def test_approaching_limit():
    """Test approaching limit detection"""
    print("Testing approaching limit detection...")

    limiter = RateLimiter(calls_per_hour=10)
    limiter.reset_all_tracking()

    # Should not be approaching limit initially
    assert limiter.is_approaching_limit() == False
    assert limiter.get_usage_percentage() == 0.0

    # Record calls to approach 80% threshold
    for i in range(8):  # 8/10 = 80%
        limiter.record_call(success=True)

    assert limiter.is_approaching_limit() == True
    assert limiter.get_usage_percentage() == 80.0

    # Test custom threshold
    assert limiter.is_approaching_limit(threshold_percent=90.0) == False
    assert limiter.is_approaching_limit(threshold_percent=70.0) == True

    print("✅ Approaching limit test passed")


def test_recent_failures():
    """Test recent failures tracking"""
    print("Testing recent failures tracking...")

    limiter = RateLimiter()
    limiter.reset_all_tracking()

    # Record some successful and failed calls
    limiter.record_call(success=True)
    limiter.record_call(success=False, error_message="Error 1")
    limiter.record_call(success=True)
    limiter.record_call(success=False, error_message="Error 2")
    limiter.record_call(success=False, error_message="Error 3")

    recent_failures = limiter.get_recent_failures(count=2)
    assert len(recent_failures) == 2

    # Should be in reverse chronological order (most recent first)
    assert recent_failures[0].error_message == "Error 3"
    assert recent_failures[1].error_message == "Error 2"

    # Test getting all failures
    all_failures = limiter.get_recent_failures(count=10)
    assert len(all_failures) == 3

    print("✅ Recent failures test passed")


def test_status_message_formatting():
    """Test status message formatting"""
    print("Testing status message formatting...")

    limiter = RateLimiter(calls_per_hour=10)
    limiter.reset_all_tracking()

    # Test normal status
    message = limiter.format_status_message()
    assert "Rate limit OK" in message
    assert "0/10 calls used" in message

    # Test approaching limit
    for i in range(8):  # 80% usage
        limiter.record_call(success=True)

    message = limiter.format_status_message()
    assert "Approaching rate limit" in message
    assert "8/10 calls used" in message

    # Test exceeded limit
    for i in range(3):  # Exceed limit
        limiter.record_call(success=True)

    message = limiter.format_status_message()
    assert "Rate limit exceeded" in message
    assert "11/10 calls" in message

    print("✅ Status message formatting test passed")


def test_reset_functionality():
    """Test reset functionality"""
    print("Testing reset functionality...")

    limiter = RateLimiter()

    # Record some calls
    for i in range(5):
        limiter.record_call(success=True)
    for i in range(2):
        limiter.record_call(success=False)

    # Verify data exists
    assert limiter.total_calls == 7
    assert len(limiter.call_history) == 7

    # Reset and verify
    reset_time = datetime.now()
    limiter.reset_all_tracking()

    assert limiter.total_calls == 0
    assert limiter.successful_calls == 0
    assert limiter.failed_calls == 0
    assert len(limiter.call_history) == 0
    assert limiter.last_reset >= reset_time

    print("✅ Reset functionality test passed")


def test_sliding_window_behavior():
    """Test sliding window behavior (simplified test)"""
    print("Testing sliding window behavior...")

    # Use very short window for testing
    limiter = RateLimiter(calls_per_hour=3, window_hours=0.001)  # ~3.6 seconds
    limiter.reset_all_tracking()

    # Fill up the limit
    for i in range(3):
        limiter.record_call(success=True)

    assert limiter.can_make_call() == False

    # Wait for window to expire (in real implementation, this would be longer)
    # For testing, we'll simulate by manually cleaning up old calls
    current_time = time.time()
    for call in limiter.call_history:
        call.timestamp = current_time - 10  # Make calls "old"

    # After cleanup, should be able to make calls again
    limiter._cleanup_old_calls()
    assert limiter.can_make_call() == True

    print("✅ Sliding window behavior test passed")


def test_boundary_conditions():
    """Test boundary conditions and edge cases"""
    print("Testing boundary conditions...")

    limiter = RateLimiter(calls_per_hour=1)  # Minimal limit
    limiter.reset_all_tracking()

    # Test exactly at limit
    limiter.record_call(success=True)
    assert limiter.can_make_call() == False

    status = limiter.get_rate_limit_status()
    assert status.calls_made == 1
    assert status.calls_remaining == 0
    assert status.limit_exceeded == True

    # Test zero calls
    limiter.reset_all_tracking()
    status = limiter.get_rate_limit_status()
    assert status.calls_made == 0
    assert status.calls_remaining == 1
    assert status.limit_exceeded == False

    print("✅ Boundary conditions test passed")


def run_all_tests():
    """Run all rate limiter tests"""
    print("🧪 Running Rate Limiter Tests")
    print("=" * 50)

    try:
        test_rate_limiter_initialization()
        test_can_make_call_basic()
        test_call_recording()
        test_rate_limit_status()
        test_time_calculations()
        test_statistics()
        test_approaching_limit()
        test_recent_failures()
        test_status_message_formatting()
        test_reset_functionality()
        test_sliding_window_behavior()
        test_boundary_conditions()

        print("=" * 50)
        print("🎉 All Rate Limiter tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
