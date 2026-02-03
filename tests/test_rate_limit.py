import pytest
from fastapi.testclient import TestClient

import app.api.rate_limit_deps as rld
from app.core.rate_limit import TokenBucketLimiter
from app.main import app


@pytest.fixture
def client():
    from app.db.pool import close_pool, init_pool

    # Initialize DB pool (TestClient doesn't trigger startup events)
    init_pool()

    yield TestClient(app)

    # Cleanup
    close_pool()


def test_search_rate_limited(client, monkeypatch):
    # Replace the global limiter with a tiny one to hit 429 quickly
    test_limiter = TokenBucketLimiter(rate_per_sec=0.0, capacity=2)  # no refill
    monkeypatch.setattr(rld, "limiter", test_limiter)

    headers = {"X-API-Key": "dev-key-1"}

    # make 3 quick requests
    r1 = client.get("/api/v1/orgs/1/employees/search", headers=headers)
    assert r1.status_code != 429

    r2 = client.get("/api/v1/orgs/1/employees/search", headers=headers)
    assert r2.status_code != 429

    r3 = client.get("/api/v1/orgs/1/employees/search", headers=headers)
    assert r3.status_code == 429
    assert "Retry-After" in r3.headers
    assert int(r3.headers["Retry-After"]) >= 1
