# app/modules/employee/service.py
from typing import Any

from fastapi import HTTPException

from app.core.security import Principal
from app.modules.employee import repository
from app.modules.employee.config import ALLOWED_COLUMNS, get_columns_for_org


def search(
    *,
    principal: Principal,
    org_id: int,
    q: str | None,
    filters: dict[str, str | None],
    limit: int,
    include_facets: bool,
    facet_limit: int,
    facet_q: str | None,
    cursor_updated_at: str | None,
    cursor_employee_id: str | None,
) -> dict[str, Any]:
    # check org_id
    if principal.org_id != org_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    # check scope
    if "employee.read" not in principal.scopes:
        raise HTTPException(status_code=403, detail="Insufficient scope")

    # get employee data
    rows = repository.search_employees(
        org_id=org_id,
        q=q,
        deptid=filters.get("deptid"),
        location=filters.get("location"),
        jobcode=filters.get("jobcode"),
        position_nbr=filters.get("position_nbr"),
        company=filters.get("company"),
        empl_status=filters.get("empl_status"),
        limit=limit,
        cursor_updated_at=cursor_updated_at,
        cursor_employee_id=cursor_employee_id,
    )

    # Dynamic columns per org + allowlist = no leakage
    columns = get_columns_for_org(org_id)
    safe_cols = [c for c in columns if c in ALLOWED_COLUMNS]
    items: list[dict[str, Any]] = []
    for r in rows:
        item = {"employee_id": str(r["employee_id"])}  # always include opaque id
        for c in safe_cols:
            item[c] = r.get(c)
        items.append(item)

    next_cursor = None
    if rows:
        last = rows[-1]
        next_cursor = {
            "updated_at": last["updated_at"].isoformat(),
            "employee_id": str(last["employee_id"]),
        }

    resp: dict[str, Any] = {"items": items, "next_cursor": next_cursor, "limit": limit}

    # Facets
    if include_facets:
        facets_position = repository.facet_positions(
            org_id=org_id,
            q=q,
            position_nbr=filters.get("position_nbr"),
            empl_status=filters.get("empl_status"),
            facet_limit=facet_limit,
            facet_q=facet_q,
        )
        resp["facets"] = {"position": facets_position}
    return resp
