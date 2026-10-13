"""Algoritmo Genético para escolher quais pokémons lutam em cada ginásio.

Cromossomo = lista de 24 genes (um por ginásio), cada gene um bitmask de 1 a
31 dizendo quais dos 5 pokémons participam daquela batalha.
"""

import random
import statistics

from config import GYM_DIFFICULTY, POKEMON_POWER, STARTING_ENERGY

GYM_LABELS = list(GYM_DIFFICULTY.keys())  # ordem fixa dos 24 genes
POKEMON_NAMES = list(POKEMON_POWER.keys())  # ordem fixa dos 5 bits
POWERS = [POKEMON_POWER[n] for n in POKEMON_NAMES]
N_POKEMON = len(POKEMON_NAMES)
N_GYMS = len(GYM_LABELS)
DIFFICULTIES = [GYM_DIFFICULTY[g] for g in GYM_LABELS]

PENALTY = 1_000_000


def random_gene():
    """Bitmask não-vazio aleatório entre 1 e 31."""
    return random.randint(1, (1 << N_POKEMON) - 1)


def random_chromosome():
    return repair([random_gene() for _ in range(N_GYMS)])


def repair(chromosome, _max_passes=5):
    """Corrige cromossomo que estourou o limite de energia, removendo
    participações pela opção que menos aumenta o tempo total."""
    chrom = list(chromosome)
    for _ in range(_max_passes):
        chrom = _repair_pass(chrom)
        if is_valid(chrom):
            break
    return chrom


def _repair_pass(chromosome):
    chrom = list(chromosome)
    counts = usage_counts(chrom)

    def cheapest_removal(pokemon_filter):
        best_choice, best_increase = None, float("inf")
        for i in pokemon_filter:
            for g_idx in range(N_GYMS):
                gene = chrom[g_idx]
                if not (gene & (1 << i)):
                    continue
                new_gene = gene & ~(1 << i)
                if new_gene == 0:
                    continue  # ginásio nunca pode ficar sem nenhum pokémon lutando
                increase = battle_time(new_gene, DIFFICULTIES[g_idx]) - battle_time(gene, DIFFICULTIES[g_idx])
                if increase < best_increase:
                    best_increase, best_choice = increase, (i, g_idx)
        return best_choice

    def cheapest_replacement(pokemon_filter):
        """Quando não dá pra só remover (ginásio ficaria vazio), troca por outro
        pokémon com energia sobrando."""
        best_choice, best_increase = None, float("inf")
        for i in pokemon_filter:
            for g_idx in range(N_GYMS):
                gene = chrom[g_idx]
                if not (gene & (1 << i)) or gene != (1 << i):
                    continue
                for j in range(N_POKEMON):
                    if j == i or counts[j] >= STARTING_ENERGY:
                        continue
                    new_gene = 1 << j
                    increase = battle_time(new_gene, DIFFICULTIES[g_idx]) - battle_time(gene, DIFFICULTIES[g_idx])
                    if increase < best_increase:
                        best_increase, best_choice = increase, (i, g_idx, j)
        return best_choice

    def reduce_one(pokemon_filter):
        """Tira 1 uso de algum pokémon da lista, removendo ou trocando."""
        choice = cheapest_removal(pokemon_filter)
        if choice is not None:
            pi, g_idx = choice
            chrom[g_idx] &= ~(1 << pi)
            counts[pi] -= 1
            return True

        replacement = cheapest_replacement(pokemon_filter)
        if replacement is not None:
            pi, g_idx, j = replacement
            chrom[g_idx] = 1 << j
            counts[pi] -= 1
            counts[j] += 1
            return True

        return False

    # limite de energia por pokémon
    for i in range(N_POKEMON):
        while counts[i] > STARTING_ENERGY:
            if not reduce_one([i]):
                break

    # pelo menos 1 pokémon precisa sobrar com energia
    for _ in range(N_POKEMON):
        if any(c < STARTING_ENERGY for c in counts):
            break
        if not reduce_one(range(N_POKEMON)):
            break

    return chrom


def usage_counts(chromosome):
    """Quantas vezes cada pokémon (por índice) luta, somado sobre todos os ginásios."""
    counts = [0] * N_POKEMON
    for gene in chromosome:
        for i in range(N_POKEMON):
            if gene & (1 << i):
                counts[i] += 1
    return counts


def battle_time(gene, difficulty):
    power_sum = sum(POWERS[i] for i in range(N_POKEMON) if gene & (1 << i))
    return difficulty / power_sum


def fitness(chromosome):
    """Soma o tempo das 24 batalhas + penalidade se violar energia. Menor é melhor."""
    total_time = sum(
        battle_time(gene, diff) for gene, diff in zip(chromosome, DIFFICULTIES)
    )

    counts = usage_counts(chromosome)
    penalty = 0
    for c in counts:
        if c > STARTING_ENERGY:
            penalty += PENALTY * (c - STARTING_ENERGY)
    if all(c >= STARTING_ENERGY for c in counts):
        # nenhum pokémon sobraria com energia >= 1 no destino
        penalty += PENALTY

    return total_time + penalty


def is_valid(chromosome):
    counts = usage_counts(chromosome)
    return all(c <= STARTING_ENERGY for c in counts) and any(c < STARTING_ENERGY for c in counts)


def tournament_select(population, fitnesses, k=3):
    idxs = random.sample(range(len(population)), k)
    best = min(idxs, key=lambda i: fitnesses[i])
    return population[best]


def crossover(parent1, parent2):
    """Crossover uniforme: cada gene vem de um dos dois pais, com 50% de chance."""
    child = [p1 if random.random() < 0.5 else p2 for p1, p2 in zip(parent1, parent2)]
    return repair(child)


def mutate_gene_bitflip(gene):
    """Liga/desliga a participação de 1 pokémon no gene."""
    bit_idx = random.randrange(N_POKEMON)
    new_gene = gene ^ (1 << bit_idx)
    return new_gene if new_gene != 0 else gene


def mutate(chromosome, mutation_rate=0.05):
    new_chrom = list(chromosome)
    for i in range(len(new_chrom)):
        if random.random() < mutation_rate:
            new_chrom[i] = mutate_gene_bitflip(new_chrom[i])
    return repair(new_chrom)


def run_ga(pop_size=100, generations=300, mutation_rate=0.05, elite_size=4, seed=None):
    if seed is not None:
        random.seed(seed)

    population = [random_chromosome() for _ in range(pop_size)]

    for _ in range(generations):
        fitnesses = [fitness(c) for c in population]

        ranked = sorted(zip(population, fitnesses), key=lambda pair: pair[1])
        new_population = [chrom for chrom, _ in ranked[:elite_size]]

        while len(new_population) < pop_size:
            p1 = tournament_select(population, fitnesses)
            p2 = tournament_select(population, fitnesses)
            child = crossover(p1, p2)
            child = mutate(child, mutation_rate)
            new_population.append(child)

        population = new_population

    fitnesses = [fitness(c) for c in population]
    best_idx = min(range(pop_size), key=lambda i: fitnesses[i])
    return population[best_idx], fitnesses[best_idx]


def run_experiment(n_runs=30, **ga_kwargs):
    """Roda o GA várias vezes e retorna melhor resultado, média e desvio-padrão."""
    results = []
    best_chrom = None
    best_fit = float("inf")

    for _ in range(n_runs):
        chrom, fit = run_ga(**ga_kwargs)
        results.append(fit)
        if fit < best_fit:
            best_fit = fit
            best_chrom = chrom

    return {
        "n_runs": n_runs,
        "best": best_fit,
        "mean": statistics.mean(results),
        "stdev": statistics.stdev(results) if n_runs > 1 else 0.0,
        "best_chromosome": best_chrom,
        "all_results": results,
    }
