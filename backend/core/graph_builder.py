from __future__ import annotations

from typing import List, Optional, Dict, Any

from backend.models.schemas import StepProof
from backend.models.flow import FlowGraph, FlowNode, FlowEdge, NodeType, EdgeType


def _safe_label(step: StepProof) -> str:

    action = (step.action or "").strip()
    if action:
        return action
    snip = (step.snippet or "").strip()
    return snip[:60] if snip else "step"


def steps_to_flow_graph(
    flow_id: str,
    steps: List[StepProof],
    *,
    version: str = "0.1.0",
    graph_meta: Optional[Dict[str, Any]] = None,
) -> FlowGraph:
    
    nodes: List[FlowNode] = []
    edges: List[FlowEdge] = []

    for i, step in enumerate(steps, start=1):
        node_id = f"n{i}"

        try:
            node_type = NodeType(step.type)
        except Exception:
            node_type = NodeType.trigger

        node = FlowNode(
            id=node_id,
            type=node_type,
            label=_safe_label(step),
            start_idx=step.start_idx,
            end_idx=step.end_idx,
            snippet=step.snippet,
            meta={
                "raw_action": step.action,
            },
        )
        nodes.append(node)

        if i > 1:
            edges.append(
                FlowEdge(
                    source=f"n{i-1}",
                    target=node_id,
                    type=EdgeType.next,
                )
            )

    return FlowGraph(
        flow_id=flow_id,
        version=version,
        nodes=nodes,
        edges=edges,
        meta=graph_meta or {},
    )
