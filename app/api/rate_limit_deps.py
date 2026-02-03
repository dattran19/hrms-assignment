from fastapi import Depends, HTTPException, Response

from app.api.deps import get_principal
from app.core.rate_limit import TokenBucketLimiter
from app.core.security import Principal

limiter = TokenBucketLimiter(
    rate_per_sec=5,
    capacity=10,
    ttl_seconds=15 * 60,  # forget unused keys after 15 minutes
    sweep_interval_seconds=60,  # cleanup once per minute
)

# Module-level singleton to satisfy linter
_principal_dependency = Depends(get_principal)


def rate_limit_dep(
    response: Response,
    principal: Principal = _principal_dependency,
) -> None:
    # safest key: per API key + org
    key = f"org:{principal.org_id}:key:{principal.caller_id}"

    try:
        allowed, retry_after, remaining_tokens = limiter.allow(key)
    except Exception:
        # Fail-open: do NOT block users if limiter is broken
        return

    # Rate limit headers for clients/debugging
    response.headers["X-RateLimit-Limit"] = str(int(limiter.capacity))
    response.headers["X-RateLimit-Remaining"] = str(max(0, int(remaining_tokens)))

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Too Many Requests",
            headers={"Retry-After": str(retry_after)},
        )
