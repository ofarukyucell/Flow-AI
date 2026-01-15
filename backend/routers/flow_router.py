from fastapi import APIRouter
import logging
import uuid

from fastapi.responses import PlainTextResponse
from backend.models.schemas import StepProof, ExtractRequest, MermaidResponse
from backend.core.mermaid_exporter import graph_to_mermaid
from backend.core.extraction_rules import extract_steps_with_proof
from backend.models.schemas import StepProof,ExtractRequest
from backend.models.flow import FlowGraph
from backend.core.graph_builder import steps_to_flow_graph
from backend.core.errors import AppError,ValidationAppError

router =APIRouter(prefix="/api",tags=["flow"])
log = logging.getLogger("flowai.flow")

@router.post("/flow",response_model=FlowGraph)
async def build_flow(req: ExtractRequest) -> FlowGraph:
    log.info("flow:start source=%s len=%d",req.source, len(req.payload))

    if req.source != "text":
        raise ValidationAppError ("şimdilik sadece 'text destekleniyor'",code="unsupported_source")
    
    raw = req.payload.strip()
    if not raw:
        raise ValidationAppError("payload boş olamaz",code="empty_payload") 
    
    if "boom" in raw.lower():
        raise AppError("iş kuralı: 'boom yasaklı anahtar'",code="rule_boom")
    
    steps=extract_steps_with_proof(raw)
    if not steps:
        steps=[
            StepProof(
                action="Taslak adım",
                start_idx=0,
                end_idx=0,
                snippet="",
                type="trigger",
            )
        ]
    flow_id = str(uuid.uuid4())
    graph=steps_to_flow_graph(flow_id=flow_id,steps=steps)

    log.info(
        "flow: done flow_id=%s steps=%d nodes=%d edges=%d",
        flow_id,len(steps),len(graph.nodes),len(graph.edges)
        )
    return graph



@router.post("/flow/mermaid",response_model=MermaidResponse)
async def flow_mermaid(req: ExtractRequest) -> MermaidResponse:
    graph = await build_flow(req)
    mermaid = graph_to_mermaid(graph)
    return MermaidResponse(ok=True,flow_id=graph.flow_id,mermaid=mermaid)

@router.post("/flow/mermaid.txt",response_class=PlainTextResponse)
async def flow_mermaid_txt(req: ExtractRequest) -> str:
    graph = await build_flow(req)
    return graph_to_mermaid(graph)

