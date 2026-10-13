import heapq
import time
import math


# configurações gerais

INTERVALO_STATUS = 10000

LIMITE_CACHE_HK = 1_500_000  # tamanho max do cache antes de descartar parte dele

INF = 10**18

# configurações do Held-Karp (heurística do A* de rota)

ITERACOES_HK = 18  # iterações de subgradiente por estado (mais = heurística mais forte e mais lenta)
ALPHA_HK = 1.50    # passo inicial do subgradiente: alpha * (UB - LB) / ||subgradiente||^2
BLOCO_SEM_MELHORIA = 4  # iterações sem melhorar antes de reduzir o passo



def carregar_mapa(nome_arquivo):

    with open(
        nome_arquivo,
        "r"
    ) as arquivo:

        return [
            list(linha.strip())
            for linha in arquivo
            if linha.strip()
        ]



def imprimir_caminho(
    mapa,
    caminho
):

    mapa_visual = [
        linha[:]
        for linha in mapa
    ]

    for linha, coluna in caminho:

        mapa_visual[linha][coluna] = '*'

    for linha in mapa_visual:

        print(''.join(linha))



def desenhar_caminho(
    mapa,
    caminho,
    arquivo_saida
):

    mapa_desenhado = [
        linha[:]
        for linha in mapa
    ]

    for linha, coluna in caminho:

        mapa_desenhado[linha][coluna] = '*'

    with open(
        arquivo_saida,
        'w'
    ) as arquivo:

        for linha in mapa_desenhado:

            arquivo.write(
                ''.join(linha) + '\n'
            )



CUSTOS = {
    'M': 200,
    'A': 30,
    'F': 15,
    'R': 5
}


def custo_terreno(
    mapa,
    posicao
):

    linha, coluna = posicao

    caractere = mapa[linha][coluna]

    return CUSTOS.get(
        caractere,
        1
    )


TERRENOS = {
    'M',
    'A',
    'F',
    'R',
    '.'
}



def encontrar_especiais(mapa):

    especiais = {}

    for linha in range(len(mapa)):

        for coluna in range(len(mapa[linha])):

            caractere = mapa[linha][coluna]

            if caractere not in TERRENOS:

                especiais[caractere] = (
                    linha,
                    coluna
                )

    return especiais



def obter_vizinhos(
    posicao,
    mapa
):

    linha, coluna = posicao

    if linha > 0:

        yield (
            linha - 1,
            coluna
        )

    if linha + 1 < len(mapa):

        if coluna < len(mapa[linha + 1]):

            yield (
                linha + 1,
                coluna
            )

    if coluna > 0:

        yield (
            linha,
            coluna - 1
        )

    if coluna + 1 < len(mapa[linha]):

        yield (
            linha,
            coluna + 1
        )



def reconstruir_caminho_astar(
    veio_de,
    atual
):

    caminho = [atual]

    while atual in veio_de:

        atual = veio_de[atual]

        caminho.append(atual)

    caminho.reverse()

    return caminho


# na prática é Dijkstra (sem heurística), mas acha o caminho ótimo do mesmo jeito
def a_estrela(
    mapa,
    inicio,
    destino
):

    fila = []

    custo_g = {
        inicio: 0
    }

    veio_de = {}

    contador = 0

    heapq.heappush(
        fila,
        (
            0,
            contador,
            inicio
        )
    )

    while fila:

        g_atual, _, atual = heapq.heappop(
            fila
        )

        if g_atual != custo_g.get(
            atual,
            INF
        ):

            continue

        if atual == destino:

            return (
                reconstruir_caminho_astar(
                    veio_de,
                    atual
                ),
                g_atual
            )

        for vizinho in obter_vizinhos(
            atual,
            mapa
        ):

            novo_g = (
                g_atual
                +
                custo_terreno(
                    mapa,
                    vizinho
                )
            )

            custo_anterior = custo_g.get(
                vizinho,
                INF
            )

            if novo_g < custo_anterior:

                custo_g[vizinho] = novo_g

                veio_de[vizinho] = atual

                contador += 1

                heapq.heappush(
                    fila,
                    (
                        novo_g,
                        contador,
                        vizinho
                    )
                )

    return None, None



def criar_grafo(mapa):

    especiais = encontrar_especiais(
        mapa
    )

    grafo = {
        no: {}
        for no in especiais
    }

    nos = list(especiais.keys())

    print("\nCriando grafo " + "-" * 40)

    print(
        "Nós especiais:",
        len(nos)
    )

    pares = (
        len(nos)
        *
        (len(nos) - 1)
        //
        2
    )

    contador_pares = 0

    for i in range(len(nos)):

        for j in range(
            i + 1,
            len(nos)
        ):

            contador_pares += 1

            if contador_pares % 100 == 0:

                print(
                    f"\rPares: "
                    f"{contador_pares:,}/"
                    f"{pares:,}",
                    end=''
                )

            a = nos[i]
            b = nos[j]

            caminho, custo = a_estrela(
                mapa,
                especiais[a],
                especiais[b]
            )

            if caminho is None:

                continue

            grafo[a][b] = {
                'custo': custo,
                'caminho': caminho
            }

            grafo[b][a] = {
                'custo': custo,
                'caminho': caminho[::-1]
            }

    print()

    print(
        "Pares processados:",
        pares
    )

    print(
        "Grafo criado."
    )

    return grafo



def preparar_problema(
    grafo,
    inicio='1',
    fim='U'
):

    inicio = str(inicio)
    fim = str(fim)

    if inicio not in grafo:

        raise ValueError(
            f"Nó inicial '{inicio}' não existe."
        )

    if fim not in grafo:

        raise ValueError(
            f"Nó final '{fim}' não existe."
        )

    todos = list(grafo.keys())

    intermediarios = [
        no
        for no in todos
        if no != inicio
        and no != fim
    ]

    nos = (
        [inicio]
        +
        intermediarios
        +
        [fim]
    )

    indice = {
        no: i
        for i, no in enumerate(nos)
    }

    n = len(nos)

    idx_inicio = indice[inicio]

    idx_fim = indice[fim]

    # matriz de custos
    custos = [
        [INF] * n
        for _ in range(n)
    ]

    for i in range(n):

        custos[i][i] = 0

    for origem in nos:

        i = indice[origem]

        for destino, dados in grafo[origem].items():

            j = indice.get(destino)

            if j is None:

                continue

            custos[i][j] = dados['custo']

    # lista de vizinhos de cada no
    vizinhos = [
        []
        for _ in range(n)
    ]

    for i in range(n):

        linha = custos[i]

        lista = vizinhos[i]

        for j in range(n):

            if i == j:

                continue

            if linha[j] < INF:

                lista.append(j)

    # cada ginasio intermediario vira um bit do mask
    inter_indices = [
        indice[no]
        for no in intermediarios
    ]

    bit_do_no = [-1] * n

    for bit, no_idx in enumerate(inter_indices):

        bit_do_no[no_idx] = bit

    todos_mask = (
        (1 << len(intermediarios))
        - 1
    )

    return {
        'nos': nos,
        'indice': indice,
        'custos': custos,
        'vizinhos': vizinhos,
        'inter_indices': inter_indices,
        'bit_do_no': bit_do_no,
        'todos_mask': todos_mask,
        'idx_inicio': idx_inicio,
        'idx_fim': idx_fim,
        'INF': INF
    }



def inserir_cache_limitado(
    cache,
    chave,
    valor
):

    cache[chave] = valor

    if len(cache) <= LIMITE_CACHE_HK:

        return

    # cache so serve pra performance, pode descartar parte dele sem problema
    quantidade_remover = max(
        1,
        LIMITE_CACHE_HK // 5
    )

    contador = 0

    for chave_remover in list(cache.keys()):

        del cache[chave_remover]

        contador += 1

        if contador >= quantidade_remover:

            break



def vertices_estado(
    atual,
    restantes_mask,
    dados
):

    """
    Estado:

        atual -> restantes -> U

    A heurística trabalha somente sobre:

        {atual} U {restantes} U {U}
    """

    vertices = [atual]

    inter_indices = dados['inter_indices']

    mask = restantes_mask

    while mask:

        bit = mask & -mask

        posicao_bit = (
            bit.bit_length() - 1
        )

        vertices.append(
            inter_indices[posicao_bit]
        )

        mask ^= bit

    fim = dados['idx_fim']

    if fim != atual:

        vertices.append(fim)

    return vertices



def construir_1tree_caminho(
    vertices,
    atual,
    fim,
    custos,
    penalidades
):

    """1-tree do caminho atual -> ... -> fim: MST(vertices - atual) + aresta
    fictícia atual-fim (custo 0) + a melhor aresta real saindo de atual.
    Usamos aresta fictícia pra transformar o caminho aberto num ciclo, onde
    todo vértice deveria ter grau 2 (daí a penalidade por multiplicador abaixo).
    Retorna (custo_penalizado, graus, norma_do_subgradiente, foi_possivel)."""

    n = len(vertices)

    if n == 0:

        return (
            INF,
            None,
            None,
            False
        )

    if n == 1:

        graus = {
            vertices[0]: 0
        }

        return (
            0,
            graus,
            0,
            True
        )

    pos = {
        no: i
        for i, no in enumerate(vertices)
    }

    raiz = atual

    fim_local = fim

    if fim_local not in pos:

        return (
            INF,
            None,
            None,
            False
        )

    outros = [
        v
        for v in vertices
        if v != raiz
    ]

    graus = {
        v: 0
        for v in vertices
    }

    # Prim, O(k^2)
    quantidade = len(outros)

    usado = [False] * quantidade

    melhor = [INF] * quantidade

    pai = [-1] * quantidade

    melhor[0] = 0

    custo_mst_penalizado = 0

    for _ in range(quantidade):

        escolhido = -1

        menor = INF

        for i in range(quantidade):

            if usado[i]:

                continue

            valor = melhor[i]

            if valor < menor:

                menor = valor

                escolhido = i

        if escolhido < 0:

            return (
                INF,
                None,
                None,
                False
            )

        if menor >= INF:

            return (
                INF,
                None,
                None,
                False
            )

        usado[escolhido] = True

        custo_mst_penalizado += menor

        pai_local = pai[escolhido]

        if pai_local >= 0:

            a = outros[
                escolhido
            ]

            b = outros[
                pai_local
            ]

            graus[a] += 1
            graus[b] += 1

        a = outros[escolhido]

        pi_a = penalidades.get(
            a,
            0.0
        )

        for j in range(quantidade):

            if usado[j]:

                continue

            b = outros[j]

            custo = custos[a][b]

            if custo >= INF:

                continue

            pi_b = penalidades.get(
                b,
                0.0
            )

            custo_modificado = (
                custo
                +
                pi_a
                +
                pi_b
            )

            if custo_modificado < melhor[j]:

                melhor[j] = custo_modificado

                pai[j] = escolhido

    # aresta fictícia atual -> fim
    custo_artificial_modificado = (
        penalidades.get(
            raiz,
            0.0
        )
        +
        penalidades.get(
            fim_local,
            0.0
        )
    )

    custo_1tree_penalizado = (
        custo_mst_penalizado
        +
        custo_artificial_modificado
    )

    graus[raiz] += 1

    graus[fim_local] += 1

    # segunda aresta real da raiz
    melhor_aresta = INF

    melhor_vizinho = -1

    pi_raiz = penalidades.get(
        raiz,
        0.0
    )

    for v in outros:

        if v == fim_local:
            # aresta real raiz-fim, diferente da ficticia, pode ser usada
            pass

        custo = custos[
            raiz
        ][
            v
        ]

        if custo >= INF:

            continue

        pi_v = penalidades.get(
            v,
            0.0
        )

        custo_modificado = (
            custo
            +
            pi_raiz
            +
            pi_v
        )

        if custo_modificado < melhor_aresta:

            melhor_aresta = (
                custo_modificado
            )

            melhor_vizinho = v

    if melhor_vizinho < 0:

        return (
            INF,
            None,
            None,
            False
        )

    custo_1tree_penalizado += (
        melhor_aresta
    )

    graus[
        raiz
    ] += 1

    graus[
        melhor_vizinho
    ] += 1

    # norma do subgradiente: soma de (grau_i - 2)^2
    norma = 0.0

    for v in vertices:

        diferenca = (
            graus[v]
            -
            2
        )

        norma += (
            diferenca
            *
            diferenca
        )

    return (
        custo_1tree_penalizado,
        graus,
        norma,
        True
    )



def held_karp_1tree(
    atual,
    restantes_mask,
    dados,
    cache,
    upper_bound=INF
):

    """Lower bound de Held-Karp pra terminar o caminho atual -> restantes -> U.
    Calcula o 1-tree várias vezes, ajustando multiplicadores pi a cada rodada
    (subgradiente) pra apertar o bound: LB(pi) = custo_1tree(pi) - 2*sum(pi).
    O maior LB encontrado é o lower bound final (custos são inteiros, então
    arredonda pra baixo no final)."""

    chave = (
        atual,
        restantes_mask
    )

    valor = cache.get(
        chave
    )

    if valor is not None:

        return valor

    custos = dados['custos']

    idx_fim = dados['idx_fim']

    if restantes_mask == 0:

        custo = custos[
            atual
        ][
            idx_fim
        ]

        if custo >= INF:

            inserir_cache_limitado(
                cache,
                chave,
                INF
            )

            return INF

        inserir_cache_limitado(
            cache,
            chave,
            custo
        )

        return custo

    vertices = vertices_estado(
        atual,
        restantes_mask,
        dados
    )

    if len(vertices) < 2:

        inserir_cache_limitado(
            cache,
            chave,
            0
        )

        return 0

    pi = {
        v: 0.0
        for v in vertices
    }

    pi[atual] = 0.0  # raiz ja tem o grau garantido pela estrutura da 1-tree

    melhor_lb = -float('inf')

    alpha = ALPHA_HK
    sem_melhoria = 0

    ub_local = upper_bound

    if (
        ub_local >= INF
        or
        ub_local <= 0
    ):

        ub_local = INF

    for _ in range(
        ITERACOES_HK
    ):

        (
            custo_penalizado,
            graus,
            norma,
            possivel
        ) = construir_1tree_caminho(
            vertices,
            atual,
            idx_fim,
            custos,
            pi
        )

        if not possivel:

            inserir_cache_limitado(
                cache,
                chave,
                INF
            )

            return INF

        soma_pi = 0.0

        for v in vertices:

            soma_pi += pi[v]

        lb = (
            custo_penalizado
            -
            2.0 * soma_pi
        )

        if lb > melhor_lb:

            melhor_lb = lb

            sem_melhoria = 0

        else:

            sem_melhoria += 1

        # grau 2 em todo mundo = achou um tour de verdade, nao so um bound
        todos_grau_2 = True

        for v in vertices:

            if graus[v] != 2:

                todos_grau_2 = False

                break

        if todos_grau_2:

            melhor_lb = max(
                melhor_lb,
                lb
            )

            break

        if norma <= 1e-12:

            break

        if (
            ub_local < INF
            and
            ub_local > lb
        ):

            diferenca_ub_lb = (
                ub_local
                -
                lb
            )

            passo = (
                alpha
                *
                diferenca_ub_lb
                /
                norma
            )

        else:

            escala = max(
                1.0,
                abs(lb)
            )

            passo = (
                alpha
                *
                escala
                /
                norma
            )

        # evita o passo explodir
        passo = min(
            passo,
            100000.0
        )

        passo = max(
            passo,
            0.000001
        )

        # pi_i += passo * (grau_i - 2): penaliza grau > 2, afrouxa grau < 2
        for v in vertices:

            if v == atual:

                continue

            subgradiente = (
                graus[v]
                -
                2
            )

            pi[v] += (
                passo
                *
                subgradiente
            )

        # reduz o passo se ficar muitas iteracoes sem melhorar (oscilando)
        if (
            sem_melhoria
            >=
            BLOCO_SEM_MELHORIA
        ):

            alpha *= 0.5

            sem_melhoria = 0

            if alpha < 0.05:

                alpha = 0.05

    if melhor_lb == -float('inf'):

        melhor_lb = 0

    if melhor_lb < 0:

        melhor_lb = 0

    # custos sao inteiros, floor evita erro numerico passar do otimo real
    melhor_lb_inteiro = math.floor(
        melhor_lb
    )

    inserir_cache_limitado(
        cache,
        chave,
        melhor_lb_inteiro
    )

    return melhor_lb_inteiro



def heuristica(
    atual,
    restantes_mask,
    dados,
    cache_held_karp,
    upper_bound=INF
):

    return held_karp_1tree(
        atual,
        restantes_mask,
        dados,
        cache_held_karp,
        upper_bound
    )



def completar_guloso_otimizado(
    dados
):

    custos = dados['custos']

    vizinhos = dados['vizinhos']

    bit_do_no = dados['bit_do_no']

    inicio = dados['idx_inicio']

    fim = dados['idx_fim']

    mask = dados['todos_mask']

    atual = inicio

    caminho = [
        atual
    ]

    custo_total = 0

    while mask:

        melhor_no = -1

        melhor_custo = INF

        for proximo in vizinhos[atual]:

            bit = bit_do_no[proximo]

            if bit < 0:

                continue

            bit_val = (
                1 << bit
            )

            if not (
                mask & bit_val
            ):

                continue

            c = custos[
                atual
            ][
                proximo
            ]

            if c < melhor_custo:

                melhor_custo = c

                melhor_no = proximo

        if melhor_no == -1:

            return None, INF

        custo_total += (
            melhor_custo
        )

        atual = melhor_no

        caminho.append(
            atual
        )

        bit = bit_do_no[
            atual
        ]

        mask ^= (
            1 << bit
        )

    custo_final = custos[
        atual
    ][
        fim
    ]

    if custo_final >= INF:

        return None, INF

    custo_total += (
        custo_final
    )

    caminho.append(
        fim
    )

    return (
        caminho,
        custo_total
    )



def construir_upper_bound(
    dados
):

    """
    Tenta várias versões da solução gulosa.

    Isso é importante porque o Held-Karp usa o upper bound
    para escolher o tamanho do passo do subgradiente.

    A busca continua exata mesmo se esta função encontrar
    somente uma solução ruim.
    """

    custos = dados['custos']

    vizinhos = dados['vizinhos']

    bit_do_no = dados['bit_do_no']

    inicio = dados['idx_inicio']

    fim = dados['idx_fim']

    intermediarios = dados[
        'inter_indices'
    ]

    candidatos_primeiro = []

    for v in vizinhos[inicio]:

        bit = bit_do_no[v]

        if bit >= 0:

            candidatos_primeiro.append(
                (
                    custos[inicio][v],
                    v
                )
            )

    candidatos_primeiro.sort()

    melhor_caminho, melhor_custo = (
        completar_guloso_otimizado(
            dados
        )
    )

    # testa alguns primeiros nos alternativos, limitado pra nao ficar caro
    limite_tentativas = min(
        16,
        len(candidatos_primeiro)
    )

    for _, primeiro in candidatos_primeiro[
        :limite_tentativas
    ]:

        mask = dados[
            'todos_mask'
        ]

        bit_primeiro = bit_do_no[
            primeiro
        ]

        if bit_primeiro < 0:

            continue

        mask ^= (
            1 << bit_primeiro
        )

        atual = primeiro

        caminho = [
            inicio,
            primeiro
        ]

        custo_total = custos[
            inicio
        ][
            primeiro
        ]

        possivel = True

        while mask:

            melhor_no = -1

            melhor_custo_aresta = INF

            for proximo in vizinhos[atual]:

                bit = bit_do_no[
                    proximo
                ]

                if bit < 0:

                    continue

                bit_val = (
                    1 << bit
                )

                if not (
                    mask & bit_val
                ):

                    continue

                custo = custos[
                    atual
                ][
                    proximo
                ]

                if custo < melhor_custo_aresta:

                    melhor_custo_aresta = custo

                    melhor_no = proximo

            if melhor_no < 0:

                possivel = False

                break

            custo_total += (
                melhor_custo_aresta
            )

            atual = melhor_no

            caminho.append(
                atual
            )

            bit = bit_do_no[
                atual
            ]

            mask ^= (
                1 << bit
            )

        if not possivel:

            continue

        custo_final = custos[
            atual
        ][
            fim
        ]

        if custo_final >= INF:

            continue

        custo_total += (
            custo_final
        )

        caminho.append(
            fim
        )

        if custo_total < melhor_custo:

            melhor_custo = (
                custo_total
            )

            melhor_caminho = caminho

    return (
        melhor_caminho,
        melhor_custo
    )



def reconstruir_caminho_fringe(
    predecessores,
    estado_final,
    inicio
):

    caminho = []

    estado = estado_final

    while estado is not None:

        atual, mask = estado

        caminho.append(
            atual
        )

        if (
            atual == inicio
            and
            mask == 0
        ):

            break

        estado = predecessores.get(
            estado
        )

    caminho.reverse()

    return caminho



def indices_para_nomes(
    caminho,
    nos
):

    return [
        nos[i]
        for i in caminho
    ]



def a_estrela_todos_ginasios(
    grafo,
    inicio='1',
    fim='U'
):

    dados = preparar_problema(
        grafo,
        inicio,
        fim
    )

    nos = dados['nos']

    custos = dados['custos']

    vizinhos = dados['vizinhos']

    bit_do_no = dados['bit_do_no']

    idx_inicio = dados['idx_inicio']

    idx_fim = dados['idx_fim']

    todos_mask = dados['todos_mask']

    (
        caminho_guloso,
        custo_guloso
    ) = construir_upper_bound(
        dados
    )

    if caminho_guloso is None:

        print(
            "Não existe solução."
        )

        return None, None

    melhor_custo = custo_guloso

    melhor_caminho_indices = (
        caminho_guloso
    )

    melhor_caminho = (
        indices_para_nomes(
            caminho_guloso,
            nos
        )
    )

    print("\nA* + Held-Karp 1-tree " + "-" * 40)

    print(
        "Nós totais:",
        len(nos)
    )

    print(
        "Nós intermediários:",
        todos_mask.bit_count()
    )

    print(
        "Solução inicial:",
        custo_guloso
    )

    print(
        "Caminho inicial:",
        " -> ".join(
            melhor_caminho
        )
    )

    cache_held_karp = {}

    total_explorados = 0

    total_gerados = 0

    total_podas = 0

    inicio_tempo = time.perf_counter()

    # cada item da fila: (f, contador, atual, mask, g); contador so desempata
    fila = []

    contador = 0

    # melhor g conhecido pra cada estado (atual, mask)
    melhor_g = {
        (
            idx_inicio,
            0
        ): 0
    }

    predecessores = {}

    h_inicial = heuristica(
        idx_inicio,
        todos_mask,
        dados,
        cache_held_karp,
        melhor_custo
    )

    if h_inicial >= INF:

        print(
            "Não existe solução possível."
        )

        return None, None

    f_inicial = h_inicial

    heapq.heappush(
        fila,
        (
            f_inicial,
            contador,
            idx_inicio,
            0,
            0
        )
    )

    print(
        "Lower bound Held-Karp inicial:",
        h_inicial
    )

    while fila:

        (
            f,
            _,
            atual,
            mask,
            g
        ) = heapq.heappop(
            fila
        )

        total_explorados += 1

        estado = (
            atual,
            mask
        )

        # ignora entrada desatualizada do heap
        g_conhecido = melhor_g.get(
            estado
        )

        if (
            g_conhecido is None
            or
            g != g_conhecido
        ):

            continue

        # f eh lower bound: se ja >= melhor_custo, esse estado nao melhora nada
        if f >= melhor_custo:

            total_podas += 1

            continue

        if mask == todos_mask:

            custo_final = custos[
                atual
            ][
                idx_fim
            ]

            if custo_final >= INF:

                total_podas += 1

                continue

            custo_total = (
                g
                +
                custo_final
            )

            if custo_total < melhor_custo:

                melhor_custo = (
                    custo_total
                )

                estado_final = (
                    atual,
                    mask
                )

                caminho_indices = (
                    reconstruir_caminho_fringe(
                        predecessores,
                        estado_final,
                        idx_inicio
                    )
                )

                caminho_indices.append(
                    idx_fim
                )

                melhor_caminho_indices = (
                    caminho_indices
                )

                melhor_caminho = (
                    indices_para_nomes(
                        caminho_indices,
                        nos
                    )
                )

                print()
                print(
                    "NOVA MELHOR SOLUÇÃO:",
                    melhor_custo
                )

                print(
                    " -> ".join(
                        melhor_caminho
                    )
                )

            continue

        for proximo in vizinhos[atual]:

            bit = bit_do_no[proximo]

            if bit < 0:  # eh o destino, so pode ir pra ele quando mask == todos_mask

                continue

            bit_val = (
                1 << bit
            )

            if mask & bit_val:  # ja visitado

                continue

            novo_mask = (
                mask
                |
                bit_val
            )

            custo_aresta = custos[
                atual
            ][
                proximo
            ]

            if custo_aresta >= INF:

                continue

            novo_g = (
                g
                +
                custo_aresta
            )

            total_gerados += 1

            if novo_g >= melhor_custo:  # poda: ja custa mais que a melhor solucao

                total_podas += 1

                continue

            novo_estado = (
                proximo,
                novo_mask
            )

            g_anterior = melhor_g.get(
                novo_estado
            )

            # ja tinha um caminho igual ou melhor pra esse mesmo estado
            if (
                g_anterior is not None
                and
                novo_g >= g_anterior
            ):

                total_podas += 1

                continue

            melhor_g[
                novo_estado
            ] = novo_g

            predecessores[
                novo_estado
            ] = (
                atual,
                mask
            )

            restantes_novo = (
                todos_mask
                ^
                novo_mask
            )

            upper_bound_novo = (
                melhor_custo
                -
                novo_g
            )

            h_novo = heuristica(
                proximo,
                restantes_novo,
                dados,
                cache_held_karp,
                upper_bound_novo
            )

            if h_novo >= INF:

                total_podas += 1

                continue

            f_novo = (
                novo_g
                +
                h_novo
            )

            if f_novo >= melhor_custo:

                total_podas += 1

                continue

            contador += 1

            heapq.heappush(
                fila,
                (
                    f_novo,
                    contador,
                    proximo,
                    novo_mask,
                    novo_g
                )
            )

        if (
            total_explorados % INTERVALO_STATUS == 0
        ):

            tempo = (
                time.perf_counter()
                -
                inicio_tempo
            )

            print("\nStatus A* " + "-" * 40)

            print(
                "Nós explorados:",
                f"{total_explorados:,}"
            )

            print(
                "Estados gerados:",
                f"{total_gerados:,}"
            )

            print(
                "Podas:",
                f"{total_podas:,}"
            )

            print(
                "Estados armazenados:",
                f"{len(melhor_g):,}"
            )

            print(
                "OPEN:",
                f"{len(fila):,}"
            )

            print(
                "Cache Held-Karp:",
                f"{len(cache_held_karp):,}"
            )

            print(
                "Melhor custo:",
                melhor_custo
            )

            print(
                "Tempo:",
                f"{tempo:.2f}s"
            )

    # heap vazio = nenhum estado restante pode bater a melhor solucao, entao e otima
    tempo = (
        time.perf_counter()
        -
        inicio_tempo
    )

    print("\nÓtimo global provado " + "-" * 40)

    print()

    print(
        "Custo ótimo:",
        melhor_custo
    )

    print(
        "Caminho:",
        " -> ".join(
            melhor_caminho
        )
    )

    print()

    print(
        "Nós explorados:",
        f"{total_explorados:,}"
    )

    print(
        "Estados gerados:",
        f"{total_gerados:,}"
    )

    print(
        "Podas:",
        f"{total_podas:,}"
    )

    print(
        "Estados armazenados:",
        f"{len(melhor_g):,}"
    )

    print(
        "Cache Held-Karp:",
        f"{len(cache_held_karp):,}"
    )

    print(
        "Tempo total:",
        f"{tempo:.2f}s"
    )

    return (
        melhor_caminho,
        melhor_custo
    )



def obter_caminho_mapa(
    grafo,
    caminho_nos
):

    caminho_mapa = []

    for i in range(
        len(caminho_nos) - 1
    ):

        origem = caminho_nos[i]

        destino = caminho_nos[i + 1]

        if (
            origem not in grafo
            or
            destino not in grafo[origem]
        ):

            raise ValueError(
                f"Não existe aresta entre "
                f"{origem} e {destino}."
            )

        trecho = grafo[
            origem
        ][
            destino
        ]['caminho']

        if i > 0:

            trecho = trecho[1:]

        caminho_mapa.extend(
            trecho
        )

    return caminho_mapa



if __name__ == "__main__":

    mapa = carregar_mapa(
        "../kanto.txt"
    )

    grafo = criar_grafo(
        mapa
    )

    print("\nGrafo " + "-" * 40)

    caminho_nos, custo = a_estrela_todos_ginasios(
        grafo,
        inicio='1',
        fim='U'
    )

    if caminho_nos is not None:

        caminho_mapa = obter_caminho_mapa(
            grafo,
            caminho_nos
        )

        print("\nCaminho ótimo no mapa " + "-" * 40)

        imprimir_caminho(
            mapa,
            caminho_mapa
        )

        desenhar_caminho(
            mapa,
            caminho_mapa,
            "mapa_caminho.txt"
        )

        print()

        print(
            "Mapa salvo em: mapa_caminho.txt"
        )