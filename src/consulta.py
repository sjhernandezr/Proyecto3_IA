# src/consulta.py
import argparse, os, datetime, json
from bn import load_edges, load_cpts, show_graph
from inferencia_enumeracion import enumeration_ask, Trace

def parse_evidence(s: str):
    ev = {}
    if not s: return ev
    for part in s.split(","):
        k, v = part.split("=")
        ev[k.strip()] = v.strip().lower()
    return ev

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edges", required=True)
    ap.add_argument("--cpts", required=True)
    ap.add_argument("--query", required=True)
    ap.add_argument("--evidence", default="")
    ap.add_argument("--outdir", default="out")
    args = ap.parse_args()

    parents = load_edges(args.edges)
    bn = load_cpts(args.cpts, parents)
    gtxt = show_graph(bn)

    ev = parse_evidence(args.evidence)
    trace = Trace(lines=[])
    dist = enumeration_ask(args.query, ev, bn, trace)

    os.makedirs(args.outdir, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(args.outdir, f"traza_{args.query}_{stamp}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("=== Grafo ===\n"); f.write(gtxt+"\n\n")
        f.write("=== Traza ===\n");  f.write("\n".join(trace.lines)+"\n\n")
        f.write("=== Resultado ===\n"); f.write(json.dumps(dist, indent=2))
    print(dist)
    print(f"Traza guardada en: {path}")

if __name__ == "__main__":
    main()
