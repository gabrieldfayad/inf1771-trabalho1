"""Mostra a busca A* no grid rodando no terminal: agente, fronteira,
visitados e caminho final, desenhados com cor a cada N passos."""

import heapq
import sys
import time

from astar_route import INF, TERRENOS, custo_terreno, obter_vizinhos, reconstruir_caminho_astar

# Códigos ANSI de cor. Formato: \033[<estilo>;<cor>m texto \033[0m
RESET = "\033[0m"
COR_CAMINHO = "\033[1;92m"      # verde brilhante, negrito — rota final
COR_AGENTE = "\033[1;97;41m"    # branco negrito sobre fundo vermelho — agente
COR_FRONTEIRA = "\033[1;96m"    # ciano brilhante — fronteira (fila do A*)
COR_VISITADO = "\033[0;34m"     # azul — já expandido
COR_ORIGEM = "\033[1;92m"       # verde negrito — origem
COR_DESTINO = "\033[1;95m"      # magenta negrito — destino
COR_GINASIO = "\033[1;93m"      # amarelo negrito — ginásio


def _cor_para_char(ch):
    if ch == "1":
        return COR_ORIGEM
    if ch == "U":
        return COR_DESTINO
    return COR_GINASIO


def _desenhar_frame(mapa, visitados, fronteira, atual, caminho, titulo):
    fronteira_set = set(fronteira)
    caminho_set = set(caminho) if caminho else set()

    linhas = []
    for r, linha in enumerate(mapa):
        chars = []
        for c, ch in enumerate(linha):
            pos = (r, c)
            if pos in caminho_set:
                chars.append(f"{COR_CAMINHO}*{RESET}")
            elif pos == atual:
                chars.append(f"{COR_AGENTE}@{RESET}")
            elif pos in fronteira_set:
                chars.append(f"{COR_FRONTEIRA}o{RESET}")
            elif pos in visitados:
                chars.append(f"{COR_VISITADO}+{RESET}")
            elif ch not in TERRENOS:
                chars.append(f"{_cor_para_char(ch)}{ch}{RESET}")
            else:
                chars.append(ch)
        linhas.append(''.join(chars))

    sys.stdout.write("\033[H\033[J")  # move cursor pro topo + limpa a tela
    print(titulo)
    print(
        f"Legenda: {COR_AGENTE}@{RESET} agente  "
        f"{COR_FRONTEIRA}o{RESET} fronteira  "
        f"{COR_VISITADO}+{RESET} visitado  "
        f"{COR_CAMINHO}*{RESET} caminho final  "
        f"{COR_ORIGEM}1{RESET} origem  "
        f"{COR_GINASIO}X{RESET} ginásio  "
        f"{COR_DESTINO}U{RESET} destino"
    )
    print()
    print('\n'.join(linhas))
    sys.stdout.flush()


def a_estrela_visual(mapa, inicio, destino, origem_label, destino_label,
                      delay=0.03, intervalo_frames=25):
    """Mesma busca de astar_route.a_estrela, mas desenhando o progresso."""

    fila = []
    custo_g = {inicio: 0}
    veio_de = {}
    contador = 0
    visitados = set()

    heapq.heappush(fila, (0, contador, inicio))

    passos = 0
    while fila:
        g_atual, _, atual = heapq.heappop(fila)

        if g_atual != custo_g.get(atual, INF):
            continue

        visitados.add(atual)
        passos += 1

        titulo = f"A* (grid) — trecho {origem_label} -> {destino_label}"

        if atual == destino:
            caminho = reconstruir_caminho_astar(veio_de, atual)
            fronteira = [item[2] for item in fila]
            _desenhar_frame(mapa, visitados, fronteira, atual, caminho,
                             titulo + " | CAMINHO ENCONTRADO")
            time.sleep(delay * 10)
            return caminho, g_atual

        if passos % intervalo_frames == 0:
            fronteira = [item[2] for item in fila]
            _desenhar_frame(mapa, visitados, fronteira, atual, None,
                             titulo + f" | custo: {g_atual}")
            time.sleep(delay)

        for vizinho in obter_vizinhos(atual, mapa):
            novo_g = g_atual + custo_terreno(mapa, vizinho)
            custo_anterior = custo_g.get(vizinho, INF)

            if novo_g < custo_anterior:
                custo_g[vizinho] = novo_g
                veio_de[vizinho] = atual
                contador += 1
                heapq.heappush(fila, (novo_g, contador, vizinho))

    return None, None


def desenhar_rota_completa(mapa, caminho_mapa, titulo="Rota completa do herói"):
    """Desenha o caminho final (já calculado) sobre o mapa, de uma vez."""
    _desenhar_frame(mapa, visitados=set(), fronteira=set(), atual=None,
                     caminho=caminho_mapa, titulo=titulo)
