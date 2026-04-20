from __future__ import annotations

from fastapi import FastAPI

from .api.routes.dashboard import router as dashboard_router
from .api.routes.feedback import router as feedback_router
from .api.routes.recommendation import router as recommendation_router
from .api.routes.training import router as training_router
from .core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.app_version)
    app.include_router(dashboard_router)
    app.include_router(recommendation_router)
    app.include_router(training_router)
    app.include_router(feedback_router)
    return app


app = create_app()
