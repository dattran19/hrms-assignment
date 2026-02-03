# app/db/pool.py
from __future__ import annotations

from psycopg_pool import ConnectionPool

from app.core.config import settings

_pool: ConnectionPool | None = None


def init_pool() -> None:
    global _pool
    if _pool is not None:
        return

    _pool = ConnectionPool(
        conninfo=settings.database_url,
        min_size=settings.db_pool_min_size,
        max_size=settings.db_pool_max_size,
        timeout=settings.db_pool_timeout,
        # Optional: max_idle can help recycle connections
        # max_idle=settings.db_pool_max_idle,
        kwargs={
            # Prefer server-side prepared statements? Usually optional.
            # "prepare_threshold": 0,
        },
        open=True,  # open pool immediately on startup
    )


def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


def get_pool() -> ConnectionPool:
    if _pool is None:
        raise RuntimeError("DB pool is not initialized")
    return _pool
