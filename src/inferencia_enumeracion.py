# src/inferencia_enumeracion.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List
from bn import BayesNet, Assign

@dataclass
class Trace:
    lines: List[str]
    def log(self, s: str): self.lines.append(s)

def normalize(dist: Dict[str, float]) -> Dict[str, float]:
    s = sum(dist.values())
    return {k: (v/s if s>0 else 0.0) for k, v in dist.items()}

def enumeration_ask(query_var: str, evidence: Assign, bn: BayesNet, trace: Trace) -> Dict[str, float]:
    order = bn.topological_order()
    trace.log(f"Consulta: P({query_var} | {evidence})")
    trace.log(f"Orden topológico: {order}")
    dist = {}
    for x in ["true","false"]:
        ev2 = dict(evidence)
        ev2[query_var] = x
        val = enumerate_all(order, ev2, bn, trace, depth=0)
        trace.log(f"Valor no normalizado para {query_var}={x}: {val}")
        dist[x] = val
    out = normalize(dist)
    trace.log(f"Distribución normalizada: {out}")
    return out

def enumerate_all(order: List[str], evidence: Assign, bn: BayesNet, trace: Trace, depth: int) -> float:
    if not order:
        return 1.0
    Y = order[0]
    rest = order[1:]
    pad = "  " * depth
    if Y in evidence:
        y = evidence[Y].lower()
        p_y = bn.nodes[Y].p_of(y, evidence)
        trace.log(f"{pad}{Y} fijada en {y}: P={p_y}")
        return p_y * enumerate_all(rest, evidence, bn, trace, depth+1)
    else:
        s = 0.0
        for y in ["true","false"]:
            ev2 = dict(evidence); ev2[Y] = y
            p_y = bn.nodes[Y].p_of(y, ev2)
            trace.log(f"{pad}Sumando {Y}={y}: P={p_y}")
            s += p_y * enumerate_all(rest, ev2, bn, trace, depth+1)
        trace.log(f"{pad}Suma total sobre {Y}: {s}")
        return s
