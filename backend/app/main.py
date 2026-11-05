"""FastAPI entry point. Run with ONE worker: the scheduler and event bus are in-process."""
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.errors import install_error_handlers

API = "/api/v1"


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="CivicFlow API", version="0.1.0", docs_url="/docs", openapi_url="/openapi.json")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    install_error_handlers(app)

    health = APIRouter(tags=["meta"])

    @health.get("/health")
    def health_check() -> dict:
        return {"status": "ok"}

    app.include_router(health, prefix=API)
    return app


app = create_app()
