# app/db/deps.py
from collections.abc import Generator
from contextlib import contextmanager

from fastapi import HTTPException
from psycopg import Connection
from psycopg_pool import PoolTimeout

from app.db.pool import get_pool


@contextmanager
def get_db_conn() -> Generator[Connection, None, None]:
    pool = get_pool()
    try:
        with pool.connection() as conn:
            yield conn
    except PoolTimeout as err:
        raise HTTPException(
            status_code=503, detail="Database busy, please retry"
        ) from err
