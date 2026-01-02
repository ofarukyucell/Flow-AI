from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.logging import setup_logging
from backend.core.request_timer import RequestTimerMiddleware
from backend.routers.health_router import router as health_router
from backend.routers.extract_router import router as extract_router
from backend.routers.flow_router import router as flow_router
from backend.core.config import settings
from backend.core.error_handler import register_exception_handlers

from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse



setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "Frontend"

if FRONTEND_DIR.exists():
    app.mount("/static",StaticFiles(directory=str(FRONTEND_DIR)),name="static")

    @app.get("/",include_in_schema=False)
    def serve_index():
        return FileResponse(str(FRONTEND_DIR / "index.html"))

app.add_middleware(RequestTimerMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(extract_router)
app.include_router(flow_router)

register_exception_handlers(app)
