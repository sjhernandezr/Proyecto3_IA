from __future__ import annotations
import csv, os
from collections import defaultdict, deque
from typing import Dict, List, Tuple

Value = str  
Assign = Dict[str, Value]

class Node:
    def __init__(self, name: str, parents: List[str]):
        self.name = name
        self.parents = parents[:]            
        self.cpt: Dict[Tuple[Value,...], Dict[Value,float]] = {} 
    def set_row(self, parent_vals: Tuple[Value,...], node_val: Value, p: float):
        node_val = node_val.lower().strip()
        self.cpt.setdefault(parent_vals, {})[node_val] = float(p)

    def p_of(self, node_val: Value, evidence: Assign) -> float:
        key = tuple(evidence[p].lower() for p in self.parents) if self.parents else tuple()
        probs = self.cpt.get(key)
        if probs is None:
            raise KeyError(f"CPT faltante para {self.name} con padres={key}")
        return float(probs[node_val.lower()])

class BayesNet:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}

    def add_node(self, name: str, parents: List[str]):
        self.nodes[name] = Node(name, parents)

    def topological_order(self) -> List[str]:
        indeg = {n:0 for n in self.nodes}
        children = defaultdict(list)
        for child, node in self.nodes.items():
            for p in node.parents:
                indeg[child] += 1
                children[p].append(child)
        q = deque([n for n,d in indeg.items() if d==0])
        order = []
        while q:
            u = q.popleft()
            order.append(u)
            for v in children[u]:
                indeg[v] -= 1
                if indeg[v]==0:
                    q.append(v)
        if len(order) != len(self.nodes):
            raise ValueError("El grafo tiene ciclos o nodos ausentes.")
        return order

def load_edges(path_edges: str) -> Dict[str, List[str]]:
    parents_map: Dict[str, List[str]] = defaultdict(list)
    nodes_seen = set()
    with open(path_edges, newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        if rd.fieldnames != ["child","parent"]:
            raise ValueError("edges.csv debe tener encabezado EXACTO: child,parent")
        for row in rd:
            ch = row["child"].strip()
            pa = row["parent"].strip()
            nodes_seen.add(ch)
            if pa and pa != "-":
                nodes_seen.add(pa)
                parents_map[ch].append(pa)
            else:
                parents_map.setdefault(ch, [])
    # asegurar que todos existen
    for n in list(nodes_seen):
        parents_map.setdefault(n, parents_map.get(n, []))
    return dict(parents_map)

def load_cpts(folder: str, parents_map: Dict[str, List[str]]) -> BayesNet:
    bn = BayesNet()
    for node, parents in parents_map.items():
        bn.add_node(node, parents)

    for node, parents in parents_map.items():
        path = os.path.join(folder, f"cpt_{node}.csv")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Falta {path}")
        with open(path, newline="", encoding="utf-8") as f:
            rd = csv.reader(f)
            header = [h.strip() for h in next(rd)]
            if "P" not in header:
                raise ValueError(f"{path}: falta columna P")
            if node not in header:
                raise ValueError(f"{path}: falta columna del nodo '{node}'")
            p_idx = header.index("P")
            node_idx = header.index(node)
            # columnas de padres en el ORDEN declarado por edges.csv
            parent_cols = []
            for p in parents:
                if p not in header:
                    raise ValueError(f"{path}: falta columna padre '{p}'")
                parent_cols.append(header.index(p))
            for row in rd:
                if not row or all(c.strip()=="" for c in row): 
                    continue
                node_val = row[node_idx].strip().lower()
                prob = float(row[p_idx])
                key = tuple(row[i].strip().lower() for i in parent_cols) if parents else tuple()
                bn.nodes[node].set_row(key, node_val, prob)
        # verificar que existan true/false y sumen 1 por combinación
        for key, vals in bn.nodes[node].cpt.items():
            if "true" not in vals or "false" not in vals:
                raise ValueError(f"{path}: falta true/false para padres={key}")
            s = vals["true"] + vals["false"]
            if abs(s-1.0) > 1e-6:
                raise ValueError(f"{path}: para {key} no suma 1 (suma {s})")
    return bn

def show_graph(bn: BayesNet) -> str:
    lines = ["=== Red Bayesiana ==="]
    for n in sorted(bn.nodes):
        lines.append(f"- {n}: padres={bn.nodes[n].parents}")
    lines.append(f"Orden topológico: {bn.topological_order()}")
    txt = "\n".join(lines)
    print(txt)
    return txt
