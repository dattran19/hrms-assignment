# app/modules/employee/repository.py
from typing import Any

from app.db.utils import fetch_all_dicts


def search_employees(
    *,
    org_id: int,
    q: str | None,
    deptid: str | None = None,
    location: str | None = None,
    jobcode: str | None = None,
    position_nbr: str | None = None,
    company: str | None = None,
    empl_status: str | None = None,
    limit: int = 20,
    cursor_updated_at: str | None = None,  # ISO string
    cursor_employee_id: str | None = None,  # UUID string
) -> list[dict[str, Any]]:
    limit = max(1, min(limit, 100))

    where = ["e.org_id = %(org_id)s"]
    params: dict[str, Any] = {"org_id": org_id, "limit": limit}

    if empl_status:
        where.append("e.empl_status = %(empl_status)s")
        params["empl_status"] = empl_status
    if company:
        where.append("e.company = %(company)s")
        params["company"] = company
    if deptid:
        where.append("e.deptid = %(deptid)s")
        params["deptid"] = deptid
    if location:
        where.append("e.location = %(location)s")
        params["location"] = location
    if jobcode:
        where.append("e.jobcode = %(jobcode)s")
        params["jobcode"] = jobcode
    if position_nbr:
        where.append("e.position_nbr = %(position_nbr)s")
        params["position_nbr"] = position_nbr

    use_fts = bool(q and q.strip())
    if use_fts:
        where.append("e.search_tsv @@ websearch_to_tsquery('simple', %(q)s)")
        params["q"] = q.strip()

    if cursor_updated_at and cursor_employee_id:
        where.append(
            "(e.updated_at, e.employee_id) < (%(cursor_updated_at)s::timestamptz, %(cursor_employee_id)s::uuid)"
        )
        params["cursor_updated_at"] = cursor_updated_at
        params["cursor_employee_id"] = cursor_employee_id

    sql = f"""
    SELECT
      e.employee_id, p.first_name, p.last_name, p.display_name, p.email_addr, p.phone,
      e.empl_status, e.company,
      c.descr AS company_descr,
      e.deptid,
      d.descr AS dept_descr,
      e.location,
      l.descr AS location_descr,
      e.jobcode,
      j.descr AS jobcode_descr,
      e.position_nbr,
      x.descr AS position_descr,
      e.reports_to_employee_id,
      e.updated_at,
      {"ts_rank(e.search_tsv, websearch_to_tsquery('simple', %(q)s)) AS rank" if use_fts else "NULL::float AS rank"}
    FROM hr_employment e
    JOIN hr_person p
      ON p.org_id = e.org_id AND p.employee_id = e.employee_id
    LEFT JOIN hr_company c
      ON c.org_id = e.org_id AND c.company = e.company
    LEFT JOIN hr_department d
      ON d.org_id = e.org_id AND d.deptid = e.deptid
    LEFT JOIN hr_location l
      ON l.org_id = e.org_id AND l.location = e.location
    LEFT JOIN hr_jobcode j
      ON j.org_id = e.org_id AND j.jobcode = e.jobcode
    LEFT JOIN hr_position x
      ON x.org_id = e.org_id AND x.position_nbr = e.position_nbr
    WHERE {" AND ".join(where)}
    ORDER BY
      e.updated_at DESC,
      e.employee_id DESC
    LIMIT %(limit)s
    """
    return fetch_all_dicts(sql, params)


def facet_positions(
    *,
    org_id: int,
    q: str | None,
    position_nbr: str | None = None,
    empl_status: str | None = None,
    facet_limit: int = 20,
    facet_q: str | None = None,
) -> list[dict[str, Any]]:
    facet_limit = max(1, min(facet_limit, 50))
    where = ["e.org_id = %(org_id)s"]
    params: dict[str, Any] = {
        "org_id": org_id,
        "facet_limit": facet_limit,
        "facet_q": facet_q.strip() if facet_q else "",
        "facet_q_like": f"%{facet_q.strip()}%" if facet_q else "%",
    }
    if empl_status:
        where.append("e.empl_status = %(empl_status)s")
        params["empl_status"] = empl_status
    if position_nbr:
        where.append("e.position_nbr = %(position_nbr)s")
        params["position_nbr"] = position_nbr
    use_fts = bool(q and q.strip())
    if use_fts:
        where.append("e.search_tsv @@ websearch_to_tsquery('simple', %(q)s)")
        params["q"] = q.strip()
    sql = f"""
    SELECT
      e.position_nbr,
      COALESCE(x.descr, '') AS position_descr,
      COUNT(*)::bigint AS count
    FROM hr_employment e
    LEFT JOIN hr_position x
      ON x.org_id = e.org_id AND x.position_nbr = e.position_nbr
    WHERE {" AND ".join(where)}
      AND (
        %(facet_q)s = ''
        OR e.position_nbr ILIKE %(facet_q_like)s
        OR x.descr ILIKE %(facet_q_like)s
      )
    GROUP BY e.position_nbr, x.descr
    ORDER BY count DESC, e.position_nbr
    LIMIT %(facet_limit)s
    """

    return fetch_all_dicts(sql, params)
