from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, ingest, reentries, risk, subscriptions
from app.core.config import get_settings
from app.core.database import init_database
from app.core.errors import register_error_handlers
from app.core.logging import configure_logging
from app.jobs.scheduler import build_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    scheduler = build_scheduler(settings)
    if settings.app_env != "test":
        scheduler.start()
    app.state.scheduler = scheduler
    yield
    if scheduler.running:
        scheduler.shutdown(wait=False)


def create_app() -> FastAPI:
    configure_logging()
    init_database(get_settings())

    app = FastAPI(
        title="WhereItFalls API",
        description="Reentry prediction, risk corridor, heatmap, and alert API.",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(reentries.router)
    app.include_router(risk.router)
    app.include_router(subscriptions.router)
    app.include_router(ingest.router)
    return app


app = create_app()
