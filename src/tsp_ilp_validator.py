"""Validador exato da rota via ILP, pra conferir o custo ótimo que o A* acha.
Usa uma aresta fictícia de custo 0 entre origem e destino pra tratar o
caminho aberto como um ciclo (formulação clássica de TSP)."""

import pulp

CBC_PATH = "/opt/homebrew/bin/cbc"


def _find_components(nodes, edges):
    adj = {n: [] for n in nodes}
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    visited = set()
    components = []
    for n in nodes:
        if n in visited:
            continue
        comp = []
        stack = [n]
        visited.add(n)
        while stack:
            cur = stack.pop()
            comp.append(cur)
            for nb in adj[cur]:
                if nb not in visited:
                    visited.add(nb)
                    stack.append(nb)
        components.append(comp)
    return components


def _extract_path(edges, origin_label, dest_label):
    adj = {}
    for a, b in edges:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)

    # evita usar a aresta ficticia como primeiro passo
    neighbors = adj[origin_label]
    start_next = neighbors[0] if neighbors[0] != dest_label else neighbors[1]

    path = [origin_label, start_next]
    prev, cur = origin_label, start_next
    while cur != dest_label:
        a, b = adj[cur]
        nxt = a if a != prev else b
        path.append(nxt)
        prev, cur = cur, nxt

    return path


def solve_tsp_ilp(labels, dist, origin_label="1", dest_label="U",
                   time_limit=120, msg=False, max_iterations=200):
    nodes = list(labels)

    def cost(a, b):
        if {a, b} == {origin_label, dest_label}:
            return 0
        return dist[(a, b)]

    pairs = [(nodes[i], nodes[j]) for i in range(len(nodes)) for j in range(i + 1, len(nodes))]

    prob = pulp.LpProblem("TSP_kanto", pulp.LpMinimize)
    x = {(a, b): pulp.LpVariable(f"x_{a}_{b}", cat="Binary") for (a, b) in pairs}

    def var(a, b):
        return x[(a, b)] if (a, b) in x else x[(b, a)]

    prob += pulp.lpSum(cost(a, b) * var(a, b) for (a, b) in pairs)

    for node in nodes:
        prob += pulp.lpSum(var(node, other) for other in nodes if other != node) == 2

    solver = pulp.COIN_CMD(path=CBC_PATH, msg=msg, timeLimit=time_limit)

    iterations = 0
    for iterations in range(1, max_iterations + 1):
        status = prob.solve(solver)
        if pulp.LpStatus[status] != "Optimal":
            return {"status": pulp.LpStatus[status], "iterations": iterations}

        edges_used = [(a, b) for (a, b) in pairs if var(a, b).value() > 0.5]
        components = _find_components(nodes, edges_used)

        if len(components) == 1:
            path = _extract_path(edges_used, origin_label, dest_label)
            total_cost = pulp.value(prob.objective)
            return {
                "status": "optimal",
                "path": path,
                "cost": total_cost,
                "iterations": iterations,
            }

        for comp in components:
            comp_set = set(comp)
            comp_pairs = [(a, b) for (a, b) in pairs if a in comp_set and b in comp_set]
            prob += pulp.lpSum(var(a, b) for (a, b) in comp_pairs) <= len(comp) - 1

    return {"status": "max_iterations_reached", "iterations": iterations}


if __name__ == "__main__":
    import time
    from astar_route import carregar_mapa, criar_grafo

    mapa = carregar_mapa("../kanto.txt")
    grafo = criar_grafo(mapa)

    labels = list(grafo.keys())
    dist = {
        (a, b): dados["custo"]
        for a in labels
        for b, dados in grafo[a].items()
    }

    t0 = time.time()
    result = solve_tsp_ilp(labels, dist, time_limit=120, msg=False)
    t1 = time.time()

    print(result)
    print("tempo total:", round(t1 - t0, 2), "s")
