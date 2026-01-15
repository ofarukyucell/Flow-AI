from __future__ import annotations

from backend.models.flow import FlowGraph

def graph_to_mermaid(graph:FlowGraph)-> str:
    lines:list[str]=["flowchart TD"]

    for n in graph.nodes:
        raw_label = n.label or n.action or ""
        label = raw_label.replace('"','\\"')

        if n.type == "decision":
            lines.append(f'{n.id}{{"{label}"}}')
        elif n.type == "terminal":
            lines.append(f'{n.id}(("{label}"))')
        else:
            lines.append(f'{n.id}["{label}"]')
        

    for e in graph.edges:
        print ("DEBUG EDGE: ", e.model_dump())
        if e.type == "next":
            lines.append(f"{e.source} --> {e.target}")
        elif e.type == "true":
            lines.append(f"{e.source} --|true|--> {e.target}")
        elif e.type =="false":
            lines.append(f"{e.source} --|false|--> {e.target}")
        else:
            lines.append(f"{e.source} --> {e.target}")


    return "\n".join(lines)