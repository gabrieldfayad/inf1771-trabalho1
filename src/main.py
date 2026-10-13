"""Resolve a rota (A*) e a alocação de pokémons (GA), e imprime o relatório."""

import time

from astar_route import (
    carregar_mapa,
    criar_grafo,
    encontrar_especiais,
    a_estrela_todos_ginasios,
    obter_caminho_mapa,
)
from genetic import run_experiment
from report import build_report, print_report
from visualizacao import a_estrela_visual, desenhar_rota_completa

MAPA_PATH = "../kanto.txt"


def main():
    print("Carregando mapa...")
    mapa = carregar_mapa(MAPA_PATH)

    print("Construindo grafo entre os 26 pontos (origem, 24 ginásios, destino)...")
    grafo = criar_grafo(mapa)

    print("\nResolvendo a rota com A* + heurística Held-Karp 1-tree...")
    t0 = time.time()
    melhor_caminho, melhor_custo = a_estrela_todos_ginasios(grafo, inicio="1", fim="U")
    tempo_rota = time.time() - t0

    if melhor_caminho is None:
        print("Não foi possível encontrar uma rota. Abortando.")
        return

    # mostra a busca animada só no primeiro trecho, os outros rodam silenciosos
    especiais = encontrar_especiais(mapa)
    origem_label, proximo_label = melhor_caminho[0], melhor_caminho[1]

    input(f"\nPressione Enter para ver a busca A* em ação no trecho "
          f"{origem_label} -> {proximo_label} (primeiro trecho da rota ótima)...")

    a_estrela_visual(
        mapa,
        especiais[origem_label],
        especiais[proximo_label],
        origem_label,
        proximo_label,
    )

    input("\nPressione Enter para ver a rota completa desenhada no mapa...")

    caminho_mapa = obter_caminho_mapa(grafo, melhor_caminho)
    desenhar_rota_completa(mapa, caminho_mapa)

    input("\nPressione Enter para rodar o Algoritmo Genético (alocação de pokémons)...")

    print("\nRodando o Algoritmo Genético (30 execuções, pop=100, gens=200)...")
    t0 = time.time()
    stats = run_experiment(n_runs=30, pop_size=100, generations=200, mutation_rate=0.1)
    tempo_ga = time.time() - t0

    print(f"\nExperimento do GA concluído em {tempo_ga:.1f}s:")
    print(f"  Melhor resultado:  {stats['best']:.3f}")
    print(f"  Média:             {stats['mean']:.3f}")
    print(f"  Desvio-padrão:     {stats['stdev']:.3f}")
    print(f"  Execuções:         {stats['n_runs']}")

    relatorio = build_report(
        route=melhor_caminho,
        route_cost=melhor_custo,
        chromosome=stats["best_chromosome"],
        expanded=None,
        route_status="optimal",
    )

    print()
    print_report(relatorio)

    print(f"\n(Tempo da rota: {tempo_rota:.1f}s | Tempo do experimento GA: {tempo_ga:.1f}s)")


if __name__ == "__main__":
    main()
