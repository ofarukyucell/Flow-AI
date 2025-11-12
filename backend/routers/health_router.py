from fastapi import APIRouter
from backend.core.errors import AppError
import logging

router = APIRouter()
log = logging.getLogger("flowai.health")


@router.get("/health")
def health_check():
    log.info("health ping")
    return {"status":"ok"}

@router.get("/boom")
def boom():
    raise AppError("demo boom", code="demo boom",http_status=418)