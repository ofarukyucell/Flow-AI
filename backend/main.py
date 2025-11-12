from fastapi import FastAPI
from backend.core.logging import setup_logging
from backend.core.request_timer import RequestTimerMiddleware
from backend.core.config import settings
from backend.core.error_handler import register_exception_handlers
from backend.routers import health_router


setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

app.add_middleware(RequestTimerMiddleware)

app.include_router(health_router.router)

register_exception_handlers(app)
