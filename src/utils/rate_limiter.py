"""
Rate limiting and API management system for OpenAI API calls.
Implements sliding window algorithm with 100 calls per hour limit.
"""
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


@dataclass
class CallRecord:
    """Record of an API call for rate limiting"""
    timestamp: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class RateLimitStatus:
    """Current rate limit status information"""
    calls_made: int
    calls_remaining: int
    reset_time: datetime
    time_until_reset: timedelta
    limit_exceeded: bool


class RateLimiter:
    """
    Rate limiter with sliding window algorithm for API call management.

    Enforces a configurable rate limit (default 100 calls per hour) using
    a sliding window approach. Tracks call history, calculates remaining
    calls, and provides reset time information.
    """

    def __init__(self, calls_per_hour: int = 100, window_hours: float = 1.0):
        """
        Initialize rate limiter with specified limits.

        Args:
            calls_per_hour: Maximum number of calls allowed per hour
            window_hours: Time window in hours for rate limiting
        """
        self.calls_per_hour = calls_per_hour
        self.window_seconds = window_hours * 3600  # Convert to seconds
        self.call_history: List[CallRecord] = []
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.last_reset = datetime.now()

    def _cleanup_old_calls(self) -> None:
        """Remove call records outside the current time window"""
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds

        # Keep only calls within the time window
        self.call_history = [
            call for call in self.call_history
            if call.timestamp > cutoff_time
        ]

    def _get_current_window_calls(self) -> List[CallRecord]:
        """Get all calls within the current time window"""
        self._cleanup_old_calls()
        return self.call_history

    def can_make_call(self) -> bool:
        """
        Check if a new API call can be made without exceeding rate limit.

        Returns:
            True if call can be made, False if rate limit would be exceeded
        """
        current_calls = self._get_current_window_calls()
        return len(current_calls) < self.calls_per_hour

    def record_call(self, success: bool = True, error_message: Optional[str] = None) -> None:
        """
        Record an API call for rate limiting tracking.

        Args:
            success: Whether the API call was successful
            error_message: Error message if call failed
        """
        call_record = CallRecord(
            timestamp=time.time(),
            success=success,
            error_message=error_message
        )

        self.call_history.append(call_record)
        self.total_calls += 1

        if success:
            self.successful_calls += 1
        else:
            self.failed_calls += 1

    def get_rate_limit_status(self) -> RateLimitStatus:
        """
        Get current rate limit status information.

        Returns:
            RateLimitStatus object with current limit information
        """
        current_calls = self._get_current_window_calls()
        calls_made = len(current_calls)
        calls_remaining = max(0, self.calls_per_hour - calls_made)
        limit_exceeded = calls_made >= self.calls_per_hour

        # Calculate reset time (when oldest call in window expires)
        if current_calls:
            oldest_call_time = min(call.timestamp for call in current_calls)
            reset_timestamp = oldest_call_time + self.window_seconds
            reset_time = datetime.fromtimestamp(reset_timestamp)
        else:
            # No calls in window, reset time is now
            reset_time = datetime.now()

        time_until_reset = max(
            timedelta(0),
            reset_time - datetime.now()
        )

        return RateLimitStatus(
            calls_made=calls_made,
            calls_remaining=calls_remaining,
            reset_time=reset_time,
            time_until_reset=time_until_reset,
            limit_exceeded=limit_exceeded
        )

    def get_time_until_next_call(self) -> timedelta:
        """
        Get time until next call can be made if rate limit is exceeded.

        Returns:
            Time until next call is allowed, or timedelta(0) if call can be made now
        """
        if self.can_make_call():
            return timedelta(0)

        status = self.get_rate_limit_status()
        return status.time_until_reset

    def get_statistics(self) -> Dict[str, any]:
        """
        Get comprehensive rate limiting statistics.

        Returns:
            Dictionary with rate limiting statistics
        """
        current_calls = self._get_current_window_calls()
        successful_in_window = sum(1 for call in current_calls if call.success)
        failed_in_window = sum(1 for call in current_calls if not call.success)

        # Calculate success rate
        total_in_window = len(current_calls)
        success_rate = (
            (successful_in_window / total_in_window * 100)
            if total_in_window > 0
            else 100.0
        )

        return {
            "calls_per_hour_limit": self.calls_per_hour,
            "window_seconds": self.window_seconds,
            "total_calls_ever": self.total_calls,
            "successful_calls_ever": self.successful_calls,
            "failed_calls_ever": self.failed_calls,
            "calls_in_current_window": total_in_window,
            "successful_in_window": successful_in_window,
            "failed_in_window": failed_in_window,
            "success_rate_percent": round(success_rate, 2),
            "can_make_call_now": self.can_make_call(),
            "last_reset": self.last_reset
        }

    def reset_all_tracking(self) -> None:
        """Reset all rate limiting tracking data"""
        self.call_history.clear()
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.last_reset = datetime.now()

    def get_recent_failures(self, count: int = 5) -> List[CallRecord]:
        """
        Get recent failed API calls for troubleshooting.

        Args:
            count: Number of recent failures to return

        Returns:
            List of recent failed call records
        """
        failed_calls = [
            call for call in self.call_history
            if not call.success
        ]

        # Sort by timestamp (most recent first) and return requested count
        failed_calls.sort(key=lambda x: x.timestamp, reverse=True)
        return failed_calls[:count]

    def is_approaching_limit(self, threshold_percent: float = 80.0) -> bool:
        """
        Check if rate limit is being approached.

        Args:
            threshold_percent: Percentage of limit to consider "approaching"

        Returns:
            True if approaching limit, False otherwise
        """
        status = self.get_rate_limit_status()
        usage_percent = (status.calls_made / self.calls_per_hour) * 100
        return usage_percent >= threshold_percent

    def get_usage_percentage(self) -> float:
        """
        Get current usage as percentage of rate limit.

        Returns:
            Usage percentage (0.0 to 100.0)
        """
        status = self.get_rate_limit_status()
        return (status.calls_made / self.calls_per_hour) * 100

    def format_status_message(self) -> str:
        """
        Format current rate limit status as user-friendly message.

        Returns:
            Formatted status message
        """
        status = self.get_rate_limit_status()

        if status.limit_exceeded:
            return (
                f"Rate limit exceeded ({status.calls_made}/{self.calls_per_hour} calls). "
                f"Next call available in {status.time_until_reset}."
            )
        elif self.is_approaching_limit():
            return (
                f"Approaching rate limit: {status.calls_made}/{self.calls_per_hour} calls used. "
                f"{status.calls_remaining} calls remaining."
            )
        else:
            return (
                f"Rate limit OK: {status.calls_made}/{self.calls_per_hour} calls used. "
                f"{status.calls_remaining} calls remaining."
            )


# Global rate limiter instance for application-wide usage
rate_limiter = RateLimiter()
