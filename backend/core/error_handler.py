import logging
import traceback
import uuid
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.core.config import settings
from backend.core.errors import AppError

log = logging.getLogger("flowai.errors")

def _error_body(*,ok=False,code="app_error",message="unexpected error",trace_id:str="",details=None):
    body = {"ok":ok,"error":{"code":code,"message":message},"trace_id":trace_id}
    if details is not None:
        body["details"]=details
    return body

def register_exception_handlers(app):
    @app.exception_handler(AppError)
    async def handle_app_error(request:Request,exc:AppError):
        trace_id = str(uuid.uuid4())
        log.warning(f"[{trace_id}] {exc.code}:{exc.message}")
        return JSONResponse(
            status_code=exc.http_status,
            content=_error_body(code=exc.code,message=exc.message,trace_id=trace_id),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(request:Request,exc:StarletteHTTPException):
        trace_id=str(uuid.uuid4())
        log.info(f"[{trace_id}] http_error {exc.status_code}:{exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(code="http_error",message=str(exc.detail),trace_id=trace_id),
        )
    
    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request:Request,exc:RequestValidationError):
        trace_id=str(uuid.uuid4())
        log.info(f"[{trace_id}]request_validation:{exc.errors()}")
        return JSONResponse(
            status_code=422,
            content=_error_body(
                code="request_validation",
                message="request validation failed",
                trace_id=trace_id,
                details=exc.errors() if settings.DEBUG else None,
            ),
        )
    
    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request,exc: Exception):
        trace_id=str(uuid.uuid4())
        tb="".join(traceback.format_exception(type(exc),exc,exc.__traceback__))
        log.error(f"[{trace_id}] unexpected: {exc}\n{tb}")
        return JSONResponse(
            status_code=500,
            content=_error_body(
                code="internal_server_error",
                message="Internal server error",
                trace_id=trace_id,
                details=str(exc) if settings.DEBUG else None
            ),
        )