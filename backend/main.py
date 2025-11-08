from fastapi import FastAPI
from backend.core.config import settings
from backend.routers import health_router


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

app.include_router(health_router.router)