# HRMS Employee Search API (FastAPI)

A high-performance, tenant-isolated Employee Search API built with FastAPI and PostgreSQL. Designed for high-scale HRMS environments, emphasizing data isolation, efficient search, and robust backpressure handling.

This assignment intentionally focuses on read-only search; write paths, indexing pipelines, and cross-service consistency are out of scope.

---

## Tech Stack

- **Language:** Python 3.11+
- **Framework:** FastAPI
- **Database:** PostgreSQL (Optimized for AWS RDS)
- **Driver:** `psycopg` (Raw SQL with `psycopg_pool` for scaling)
- **Search:** Postgres Full-Text Search (`tsvector` + `GIN` index)
- **Linting/Formatting:** [Ruff](https://github.com/astral-sh/ruff) (Rust-powered)
- **Testing:** `pytest`
- **DevOps:** Docker (Multi-stage, slim image, non-root user)

---

## Core Features

### Strict Tenant Isolation
Isolation is enforced at both the Service Layer and SQL levels using `org_id`. Cross-organization requests are rejected with a `403 Forbidden` before any DB execution occurs.

### Full-Text Search (FTS)
Utilizes native PostgreSQL FTS instead of overhead-heavy external engines.
- Precomputed `tsvector` with weighted fields (e.g., Name > Job Title).
- Uses `websearch_to_tsquery` for intuitive, Google-like search syntax.

### Keyset Pagination (Cursor-based)
Optimized for large datasets and frequent updates.
- **Ordering:** `(updated_at DESC, employee_id DESC)`
- **Benefit:** Avoids `OFFSET` performance degradation and zero "data drifting" (duplicate or skipped records) when data changes during browsing.

### Rate Limiting & Safety
- **Token Bucket:** In-memory rate limiting with accurate `Retry-After` headers.
- **Backpressure:** Managed via `psycopg_pool`. DB pool exhaustion results in a clean `503 Service Unavailable`.
- **Fail-Open:** Rate limiter is designed to fail-open to ensure service availability if the limiter encounters issues.

---

## Configuration

The application uses `pydantic-settings`. Create a `.env` file in the project root.

### `.env.example`
```env
# App Configuration
SERVICE_NAME=hrms
ENV=local
LOG_LEVEL=INFO

# Database (AWS RDS or Local)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=app
DB_USER=app
DB_PASSWORD=app

# Pool / Backpressure
DB_POOL_MIN_SIZE=1
DB_POOL_MAX_SIZE=10
DB_POOL_TIMEOUT=2

# Rate Limiting
RATE_LIMIT_RPM=120

# Demo Authentication
API_KEY=dev-key-1
```

---

## Running with Docker

This setup uses a multi-stage slim build with a non-root user.

### 1. Build & Run
```bash
docker-compose up --build hrms-app
```

### 2. Access the API
- **API Base:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health (Liveness only)

---

## API Usage

### Search Employees
```bash
curl -H "X-API-Key: dev-key-1" \
  "http://localhost:8000/api/v1/orgs/1/employees/search?q=engineer"
```

### Dynamic Response Columns
The API respects per-org column visibility configurations. While `employee_id` (UUID) is always returned, other fields are dynamically filtered based on the organization's allowlist.

---

## Testing & Quality

### Running Tests
```bash
python -m pytest -v
```

**Coverage includes:**
- Keyset pagination correctness (no duplicates).
- Rate limiting (429 status + Retry-After header).
- Tenant isolation (Cross-org rejection).

### Linting (Ruff)
This project adheres to strict formatting rules. To check and fix formatting:

```bash
ruff check --fix .
ruff format .
```

---

## Design Notes & Tradeoffs

- **Postgres FTS:** Chosen over Elasticsearch to minimize infrastructure complexity. The search backend is isolated behind the repository layer, allowing a future swap to Elasticsearch/OpenSearch if fuzzy matching, advanced ranking, or heavy faceting becomes a requirement.
- **No ORM:** Raw SQL is used to keep queries explicit and utilize PostgreSQL-specific features like tuple comparison for pagination.
- **In-Memory Rate Limiter:** A standard-library token bucket is used for the assignment scope.  
  This implementation is **per-process** and does not coordinate across replicas.  
  For horizontal scaling, the limiter can be replaced with a shared backend such as Redis or enforced at the API gateway/WAF layer.
