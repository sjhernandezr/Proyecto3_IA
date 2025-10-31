import csv, os, itertools, sys
from collections import defaultdict, deque

def cargar_edges(path):
    padres = defaultdict(list)
    nodos = set()
    with open(path, newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        if rd.fieldnames != ["child","parent"]:
            raise ValueError("edges.csv debe tener encabezado EXACTO: child,parent")
        for row in rd:
            h = row["child"].strip()
            p = row["parent"].strip()
            if not h:
                raise ValueError("Hay un child vacío en edges.csv")
            nodos.add(h)
            if p and p != "-":
                nodos.add(p)
                padres[h].append(p)
            else:
                padres.setdefault(h, [])
    # asegurar que todas las raíces aparezcan
    for n in list(nodos):
        padres.setdefault(n, padres.get(n, []))
    # ordenar lista de padres para consistencia
    return {n: padres[n] for n in padres}

def orden_topologico(padres_map):
    indeg = {n: 0 for n in padres_map}
    hijos = defaultdict(list)
    for ch, ps in padres_map.items():
        for p in ps:
            if p not in indeg:
                raise ValueError(f"El padre '{p}' no está declarado como nodo en edges.csv")
            indeg[ch] += 1
            hijos[p].append(ch)
    q = deque([n for n, d in indeg.items() if d == 0])
    orden = []
    while q:
        u = q.popleft()
        orden.append(u)
        for v in hijos[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    if len(orden) != len(indeg):
        raise ValueError("El grafo tiene ciclos o nodos ausentes.")
    return orden

def todas_combinaciones(nombres):
    # devuelve lista de tuplas ('true'/'false', ...) en orden de 'nombres'
    vals = ["true","false"]
    for combo in itertools.product(vals, repeat=len(nombres)):
        yield combo

def cargar_cpt(path_cpt, nodo, padres):
    if not os.path.exists(path_cpt):
        raise FileNotFoundError(f"No existe {path_cpt}")
    with open(path_cpt, newline="", encoding="utf-8") as f:
        rd = csv.reader(f)
        header = next(rd)
        header = [h.strip() for h in header]
        if "P" not in header:
            raise ValueError(f"{path_cpt}: falta la columna P")
        p_idx = header.index("P")
        if nodo not in header:
            raise ValueError(f"{path_cpt}: falta columna del nodo '{nodo}'")
        nodo_idx = header.index(nodo)

        # parent cols = header antes de P, quitando nodo
        parent_cols = [h for h in header[:p_idx] if h != nodo]
        if set(parent_cols) != set(padres):
            raise ValueError(
                f"{path_cpt}: columnas de padres {parent_cols} no coinciden con edges {padres}"
            )
        # mapea combinación de padres (en el orden 'padres') -> {'true':p,'false':p}
        tabla = defaultdict(dict)
        for row in rd:
            if not row or all(c.strip()=="" for c in row):
                continue
            node_val = row[nodo_idx].strip().lower()
            if node_val not in ("true","false"):
                raise ValueError(f"{path_cpt}: valor inválido para {nodo}: {node_val}")
            try:
                pval = float(row[p_idx])
            except:
                raise ValueError(f"{path_cpt}: P debe ser numérico")
            if not (0.0 <= pval <= 1.0):
                raise ValueError(f"{path_cpt}: P fuera de [0,1]: {pval}")

            # construir clave de padres en el ORDEN de 'padres'
            key = tuple( (row[header.index(p)].strip().lower() if p in header else None) for p in padres )
            if any(v not in ("true","false") for v in key):
                raise ValueError(f"{path_cpt}: valores de padres deben ser true/false. Encontrado: {key}")
            if node_val in tabla[key]:
                raise ValueError(f"{path_cpt}: fila duplicada para {key} y {nodo}={node_val}")
            tabla[key][node_val] = pval

        # validar cobertura completa y suma a 1
        for combo in todas_combinaciones(padres):
            if combo not in tabla:
                raise ValueError(f"{path_cpt}: falta combinación de padres {combo}")
            probs = tabla[combo]
            if "true" not in probs or "false" not in probs:
                raise ValueError(f"{path_cpt}: falta true/false para {combo}")
            s = probs["true"] + probs["false"]
            if abs(s - 1.0) > 1e-6:
                raise ValueError(f"{path_cpt}: para {combo} las probabilidades no suman 1 (suman {s})")
        return tabla  # usable luego para inferencia

def validar_reglas_proyecto(padres_map):
    n = len(padres_map)
    if n < 6:
        raise ValueError(f"Regla: mínimo 6 variables. Tienes {n}")
    con_ge3 = [v for v, ps in padres_map.items() if len(ps) >= 3]
    con_1 = [v for v, ps in padres_map.items() if len(ps) == 1]
    if len(con_ge3) != 1:
        raise ValueError(f"Regla: exactamente 1 nodo con ≥3 padres. Encontrados: {con_ge3}")
    if len(con_1) > 1:
        raise ValueError(f"Regla: máximo 1 nodo con 1 padre. Encontrados: {con_1}")
    return con_ge3[0], (con_1[0] if con_1 else None)

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--edges", required=True, help="Ruta a data/edges.csv")
    ap.add_argument("--cpts", required=True, help="Carpeta data/ con cpt_*.csv")
    args = ap.parse_args()

    print("== Cargando edges…")
    padres_map = cargar_edges(args.edges)
    for nodo, ps in sorted(padres_map.items()):
        print(f"- {nodo}: padres={ps}")

    print("\n== Reglas del proyecto…")
    nodo_ge3, nodo_1 = validar_reglas_proyecto(padres_map)
    print(f"OK: nodo con ≥3 padres: {nodo_ge3}")
    print(f"OK: nodo(s) con 1 padre: {([nodo_1] if nodo_1 else [])}")

    print("\n== Orden topológico…")
    orden = orden_topologico(padres_map)
    print("Orden:", orden)

    print("\n== Validando CPT por nodo…")
    errores = 0
    for nodo, ps in sorted(padres_map.items()):
        path = os.path.join(args.cpts, f"cpt_{nodo}.csv")
        try:
            tabla = cargar_cpt(path, nodo, ps)
            total_combos = 2**len(ps)
            print(f"OK: {nodo} | padres={len(ps)} | combos={total_combos} | archivo={os.path.basename(path)}")
        except Exception as e:
            errores += 1
            print(f"[ERROR] {nodo}: {e}")

    if errores == 0:
        print("\n=== VALIDACIÓN COMPLETA: todo OK ===")
        sys.exit(0)
    else:
        print(f"\n=== VALIDACIÓN CON {errores} ERROR(ES). Corrige y vuelve a correr. ===")
        sys.exit(1)

if __name__ == "__main__":
    main()