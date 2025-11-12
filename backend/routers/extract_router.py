from fastapi import APIRouter
import logging
import uuid

from backend.models.schemas import ExtractRequest, ExtractResponse
from backend.core.errors import AppError, ValidationAppError

router=APIRouter (prefix="/api" , tags=["extract"])
log = logging.getLogger("flowai.extract")

@router.post("/extract",response_model=ExtractResponse)
async def extract(req: ExtractRequest) -> ExtractResponse:
    log.info("extract:start source=%s len= %d",req.source, len(req.payload))

    if req.source != "text":
        raise ValidationAppError("şimdilik sadece 'text' destekleniyor",code="unsupportes_source")
    
    raw = req.payload.strip()
    if not raw:
        raise ValidationAppError("payload boş olamaz", code="empty_payload") 
    
    if "boom" in raw.lower():
        raise AppError("iş kuralı: 'boom' yasaklı anahtar", code="rule_boom")
    
    steps = [s.strip() for s in raw.replace(">","->").split("->")if s.strip()]
    if not steps:
        steps=["1) Taslak adım"]

    flow_id = str(uuid.uuid4())

    log.info("extract:done flow_id=%s steps=%d",flow_id,len(steps))

    return ExtractResponse(ok=True,flow_id=flow_id , steps=steps)    