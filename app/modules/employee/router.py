from fastapi import APIRouter, Depends, Query

from app.api.deps import get_principal
from app.api.rate_limit_deps import rate_limit_dep
from app.core.security import Principal
from app.modules.employee import service

router = APIRouter(prefix="/orgs/{org_id}/employees", tags=["employees"])

# Module-level singleton to satisfy linter
_principal_dependency = Depends(get_principal)


@router.get("/search", dependencies=[Depends(rate_limit_dep)])
def search_employees(
    org_id: int,
    q: str | None = Query(default=None),
    deptid: str | None = None,
    location: str | None = None,
    jobcode: str | None = None,
    position_nbr: str | None = None,
    company: str | None = None,
    empl_status: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    include_facets: bool = Query(default=False),
    facet_limit: int = Query(default=20, ge=1, le=50),
    facet_q: str | None = Query(default=None),
    cursor_updated_at: str | None = None,
    cursor_employee_id: str | None = None,
    principal: Principal = _principal_dependency,
):
    return service.search(
        principal=principal,
        org_id=org_id,
        q=q,
        filters={
            "deptid": deptid,
            "location": location,
            "jobcode": jobcode,
            "company": company,
            "position_nbr": position_nbr,
            "empl_status": empl_status,
        },
        limit=limit,
        include_facets=include_facets,
        facet_limit=facet_limit,
        facet_q=facet_q,
        cursor_updated_at=cursor_updated_at,
        cursor_employee_id=cursor_employee_id,
    )
