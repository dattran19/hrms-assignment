from typing import Any

from app.db.deps import get_db_conn


def fetch_all_dicts(sql: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Execute a query and return rows as list[dict[column, value]].
    Intended for read-only queries.
    """
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            cols = [d.name for d in cur.description]
            return [dict(zip(cols, row, strict=True)) for row in cur.fetchall()]
