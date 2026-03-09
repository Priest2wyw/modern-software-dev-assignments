from __future__ import annotations

from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .db import DatabaseError, init_db
from .routers import action_items, notes
from .services.extract import ExtractionError

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    settings = app.state.settings
    logger.info(
        "Application started with db_path=%s ollama_host=%s ollama_model=%s",
        settings.db_path,
        settings.ollama_host,
        settings.ollama_model,
    )
    yield


def create_app() -> FastAPI:
    app_settings = get_settings()
    app = FastAPI(title=app_settings.app_title, lifespan=lifespan)
    app.state.settings = app_settings

    @app.exception_handler(DatabaseError)
    async def handle_database_error(_: Request, exc: DatabaseError) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": str(exc)})

    @app.exception_handler(ExtractionError)
    async def handle_extraction_error(_: Request, exc: ExtractionError) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        html_path = Path(app.state.settings.frontend_dir) / "index.html"
        return html_path.read_text(encoding="utf-8")

    app.include_router(notes.router)
    app.include_router(action_items.router)
    app.mount("/static", StaticFiles(directory=str(app_settings.frontend_dir)), name="static")
    return app


app = create_app()
