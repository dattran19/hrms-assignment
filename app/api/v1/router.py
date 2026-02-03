from fastapi import APIRouter

from app.modules.employee.router import router as employee_router

v1_router = APIRouter()

@v1_router.get("/health")
def v1_health():
    return {"ok": True, "version": "v1"}

v1_router.include_router(employee_router)
