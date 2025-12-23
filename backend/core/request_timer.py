from time import perf_counter
from typing import Callable
import logging

from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

_request_logger = logging.getLogger("flowai.request")

class RequestTimerMiddleware(BaseHTTPMiddleware):
    """
    Her http isteğinin çalışmasını zamanlar vetek satır log yazar.
    format: METHOD PATH STATUS duration_ms
    örn: GET /health 200 3.12ms
    """
    async def dispatch(self, request:Request, call_next:Callable) -> Response:
        start = perf_counter()
        try:
            response = await call_next(request)
        
        except Exception:
            duration_ms = (perf_counter() - start) * 1000
            _request_logger.warning(
                "%s %s %s %.2fms",
                request.method,
                request.url.path,
                500,
                duration_ms,
                extra={"path":request.url.path},
            )
            raise

        duration_ms = (perf_counter()-start) * 1000
        _request_logger.info(
            "%s %s %s %.2fms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            extra = {"path": request.url.path},
        )
        return response