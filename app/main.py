from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.db.pool import close_pool, init_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_pool()
    yield
    # Shutdown
    close_pool()


def create_app() -> FastAPI:
    app = FastAPI(title="HRMS", version="0.1.0", lifespan=lifespan)

    # Non-versioned health check (handy for infra / readiness probes)
    @app.get("/health")
    def health():
        return {"ok": True}

    app.include_router(api_router)
    return app


app = create_app()
