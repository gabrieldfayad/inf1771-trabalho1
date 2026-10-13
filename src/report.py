"""Monta e imprime o relatório final: ordem de visita, pokémon usado em cada
batalha, energia final de cada um, custo da rota, das batalhas e total."""

from genetic import GYM_LABELS, POKEMON_NAMES, battle_time, usage_counts
from config import GYM_DIFFICULTY, STARTING_ENERGY


def gene_to_names(gene):
    return [POKEMON_NAMES[i] for i in range(len(POKEMON_NAMES)) if gene & (1 << i)]


def build_report(route, route_cost, chromosome, expanded=None, route_status="optimal",
                  route_lower_bound=None):
    """`route`: lista de rótulos ["1", ..., "U"] na ordem visitada.
    `chromosome`: lista de 24 genes na ordem fixa de GYM_LABELS (não a ordem da rota)."""

    gene_by_label = dict(zip(GYM_LABELS, chromosome))
    visit_order = [label for label in route if label in GYM_LABELS]

    battles = []
    total_battle_cost = 0
    for label in visit_order:
        gene = gene_by_label[label]
        pokemons = gene_to_names(gene)
        t = battle_time(gene, GYM_DIFFICULTY[label])
        total_battle_cost += t
        battles.append({
            "gym": label,
            "difficulty": GYM_DIFFICULTY[label],
            "pokemons": pokemons,
            "time": t,
        })

    counts = usage_counts(chromosome)
    final_energy = {
        POKEMON_NAMES[i]: STARTING_ENERGY - counts[i] for i in range(len(POKEMON_NAMES))
    }

    return {
        "route_status": route_status,
        "route": route,
        "visit_order": visit_order,
        "route_cost": route_cost,
        "route_lower_bound": route_lower_bound,
        "battles": battles,
        "battle_cost_total": total_battle_cost,
        "final_energy": final_energy,
        "total_cost": route_cost + total_battle_cost,
        "expanded_states": expanded,
    }


def print_report(report):
    print("\nRelatório final " + "-" * 40)

    status = report["route_status"]
    if status == "optimal":
        print("Rota: ÓTIMA (A* completou a busca; garantia de otimalidade).")
    else:
        gap = None
        if report["route_lower_bound"]:
            gap = 100 * (report["route_cost"] - report["route_lower_bound"]) / report["route_lower_bound"]
        print(f"Rota: melhor solução encontrada dentro do orçamento de tempo "
              f"(NÃO comprovadamente ótima).")
        if gap is not None:
            print(f"  Cota inferior comprovada: {report['route_lower_bound']:.2f} "
                  f"| gap em relação à solução encontrada: {gap:.2f}%")

    print(f"\nOrdem de visita aos {len(report['visit_order'])} ginásios:")
    print("  1 -> " + " -> ".join(report["visit_order"]) + " -> U")

    print("\nBatalhas:")
    for b in report["battles"]:
        print(f"  Ginásio {b['gym']} (dificuldade {b['difficulty']}): "
              f"{', '.join(b['pokemons'])} | tempo = {b['time']:.3f} min")

    print("\nEnergia final de cada pokémon:")
    for name, energy in report["final_energy"].items():
        estado = "acordado" if energy >= 1 else "hibernando"
        print(f"  {name}: {energy} ({estado})")

    if report["expanded_states"] is not None:
        print(f"\nEstados expandidos pelo A* (rota): {report['expanded_states']}")

    print(f"\nCusto da rota (Crota):          {report['route_cost']:.3f} min")
    print(f"Custo total das batalhas (Cbat): {report['battle_cost_total']:.3f} min")
    print(f"CUSTO TOTAL (Crota + Cbat):      {report['total_cost']:.3f} min")
