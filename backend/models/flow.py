from __future__ import annotations

from enum import Enum
from typing import List,Optional,Dict,Any
from pydantic import BaseModel, Field

class NodeType(str, Enum):
    action = "action"
    decision = "decision"
    terminal = "terminal"
    trigger = "trigger"

class FlowNode(BaseModel):
    id: str
    type: NodeType
    label: str

    start_idx: int
    end_idx: int
    snippet: str

    meta: Dict[str,Any]=Field(default_factory=dict)

class EdgeType(str, Enum):
    next = "next"
    true = "true"
    false = "false"
    jump = "jump"

class FlowEdge(BaseModel):
    source: str
    target: str
    type: EdgeType=EdgeType.next
    label: Optional[str]=None
    meta: Dict[str, Any]=Field(default_factory=dict)

class FlowGraph(BaseModel):
    flow_id:str
    version:str = "0.1.0"
    nodes:List[FlowNode]
    edges:List[FlowEdge] = Field(default_factory=list)
    meta: Dict[str,Any]=Field(default_factory=dict)