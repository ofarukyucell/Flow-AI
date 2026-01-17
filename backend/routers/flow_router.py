from fastapi import Body,APIRouter
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
EXTRACT_EXAMPLE={
    "source":"text",
    "payload":"Eğer email boşsa uyar. Kaydol. Sonlandır.",
    "options":{}
}

MERMAID_TXT_EXAMPLE= """flowchart TD
n1{"eğer email"}
n2["kaydol"]
n3(("sonlandır"))
n1 --|true|--> n2
n1 --|false|--> n3
n2 --> n3
"""
log = logging.getLogger("flowai.flow")

@router.post("/flow",
             response_model=FlowGraph,
             summary="Build FlowGraph",
             description=(
                 "Verilen Türkçe metinden adımları (StepProof) çıkarır, FlowGraph (nodes/edges) üretir. \n\n"
                 "Notlar:\n"
                 "- Şimdilik sadece source 'text' desteklenir.\n"
                 "- payload boş olamaz.\n"
                 "- 'boom' anahtar kelimesi iş kuralı gereği yasaklıdır."
             ),
             response_description="FlowGraph (nodes + edges) JSON"
             )
async def build_flow(req: ExtractRequest=Body(...,example=EXTRACT_EXAMPLE)) -> FlowGraph:
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



@router.post(
    "/flow/mermaid",
    response_model=MermaidResponse,
    summary="Export Mermaid (JSON)",
    description=(
        "FlowGraph üretir ve Mermaid flowchart çıktısını JSON içinde döner.\n\n"
        "Dönüş alanları:\n"
        "- ok: işlem başarılı mı\n"
        "- flow_id: oluşturulan flow id\n"
        "- mermaid: mermaid flowchart metni"
    ),
    response_description="Mermaid text wrapped in JSON",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "ok": True,
                        "flow_id": "a0bb89c7-87ad-4c93-b70b-3a07e0410105",
                        "mermaid": MERMAID_TXT_EXAMPLE.strip()
                    }
                }
            }
                 
        }
    }     
    
 )
async def flow_mermaid(req: ExtractRequest=Body(...,example=EXTRACT_EXAMPLE)) -> MermaidResponse:
    graph = await build_flow(req)
    mermaid = graph_to_mermaid(graph)
    return MermaidResponse(ok=True,flow_id=graph.flow_id,mermaid=mermaid)



@router.post(
        "/flow/mermaid.txt",
        response_class=PlainTextResponse,
        summary="Export Mermaid (plain text)",
    description="Mermaid flowchart çıktısını düz metin (text/plain) olarak döner.",
    response_description="Mermaid flowchart text",
    responses={
        200: {
            "content": {
                "text/plain": {
                    "example": MERMAID_TXT_EXAMPLE.strip()
                }
            }
        }
    }
)
async def flow_mermaid_txt(req: ExtractRequest=Body(...,example=EXTRACT_EXAMPLE)) -> str:
    graph = await build_flow(req)
    return graph_to_mermaid(graph)

