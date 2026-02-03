from __future__ import annotations

import math
import threading
import time
from dataclasses import dataclass


@dataclass
class Bucket:
    tokens: float
    last: float  # monotonic timestamp (also works as "last_seen")


class TokenBucketLimiter:
    """
    Token bucket limiter:
      - Allows bursts up to `capacity`
      - Sustains `rate_per_sec` over time
      - In-memory (per process)
      - TTL cleanup to prevent unbounded memory growth
      - Accurate Retry-After calculation
    """

    def __init__(
        self,
        *,
        rate_per_sec: float,
        capacity: int,
        ttl_seconds: float = 15 * 60,  # evict buckets idle for 15 minutes
        sweep_interval_seconds: float = 60,  # run cleanup at most once per minute
    ) -> None:
        self.rate = float(rate_per_sec)
        self.capacity = float(capacity)
        self.ttl_seconds = float(ttl_seconds)
        self.sweep_interval_seconds = float(sweep_interval_seconds)
        self._lock = threading.Lock()
        self._buckets: dict[str, Bucket] = {}
        self._last_sweep = time.monotonic()

    def _sweep_if_needed(self, now: float) -> None:
        # Run cleanup occasionally (avoids a background thread)
        if (now - self._last_sweep) < self.sweep_interval_seconds:
            return
        cutoff = now - self.ttl_seconds
        # Delete keys that haven't been seen recently
        to_delete = [k for k, b in self._buckets.items() if b.last < cutoff]
        for k in to_delete:
            del self._buckets[k]
        self._last_sweep = now

    def allow(self, key: str, cost: float = 1.0) -> tuple[bool, int, float]:
        """
        Returns (allowed, retry_after_seconds, remaining_tokens).
        retry_after_seconds:
          - 0 if allowed
          - else: number of seconds client should wait before retrying
        remaining_tokens:
          - number of tokens remaining in the bucket after this request
        """
        now = time.monotonic()

        with self._lock:
            # TTL cleanup
            self._sweep_if_needed(now)

            b = self._buckets.get(key)
            if b is None:
                # Start full so the user can burst immediately
                b = Bucket(tokens=self.capacity, last=now)
                self._buckets[key] = b

            # Refill based on elapsed time
            elapsed = now - b.last
            if elapsed > 0:
                b.tokens = min(self.capacity, b.tokens + elapsed * self.rate)

            # Always refresh last_seen for TTL accuracy
            b.last = now  # also updates "last_seen"

            # Allow if enough tokens
            if b.tokens >= cost:
                b.tokens -= cost
                return True, 0, b.tokens

            # Not enough tokens: compute accurate retry-after
            if self.rate <= 0:
                # No refill possible: effectively "blocked"
                return (
                    False,
                    60,
                    b.tokens,
                )  # a safe default; could also be a large number

            missing = cost - b.tokens  # how many tokens are needed
            retry_after = math.ceil(missing / self.rate)

            # If due to floating precision it's already basically available, return 1 as a safe value
            # (HTTP Retry-After is integer seconds)
            return False, max(1, int(retry_after)), b.tokens
