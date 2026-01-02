from __future__ import annotations

from backend.models.flow import FlowGraph

def graph_to_mermaid(graph:FlowGraph)-> str:
    lines:list[str]=["flowchart TD"]

    for n in graph.nodes:
        label=(n.label or "").replace('"','\\"')
        lines.append(f'{n.id}["{label}"]')

    for e in graph.edges:
        lines.append(f"{e.source}-->{e.target}")

    return "\n".join(lines)