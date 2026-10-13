"""DP exata pra conferir se o GA acha o ótimo global da alocação de pokémons.
Estado: energia restante de cada pokémon (0..6), 7^5 combinações."""

from config import GYM_DIFFICULTY, POKEMON_POWER, STARTING_ENERGY

GYM_LABELS = list(GYM_DIFFICULTY.keys())
POKEMON_NAMES = list(POKEMON_POWER.keys())
POWERS = [POKEMON_POWER[n] for n in POKEMON_NAMES]
N_POKEMON = len(POKEMON_NAMES)
DIFFICULTIES = [GYM_DIFFICULTY[g] for g in GYM_LABELS]

E = STARTING_ENERGY + 1  # 7 valores possiveis (0..6) por pokemon
N_STATES = E ** N_POKEMON

POWER_SUM_FOR_MASK = [0.0] * 32
for mask in range(1, 32):
    POWER_SUM_FOR_MASK[mask] = sum(POWERS[i] for i in range(N_POKEMON) if mask & (1 << i))


def encode(energies):
    idx = 0
    for e in reversed(energies):
        idx = idx * E + e
    return idx


def decode(idx):
    energies = []
    for _ in range(N_POKEMON):
        energies.append(idx % E)
        idx //= E
    return tuple(energies)


def solve_exact():
    INF = float("inf")
    dp = [INF] * N_STATES
    dp[encode((STARTING_ENERGY,) * N_POKEMON)] = 0.0

    for difficulty in DIFFICULTIES:
        new_dp = [INF] * N_STATES
        for idx, cost_so_far in enumerate(dp):
            if cost_so_far == INF:
                continue
            energies = decode(idx)
            for mask in range(1, 32):
                if all((mask & (1 << i)) == 0 or energies[i] > 0 for i in range(N_POKEMON)):
                    new_energies = list(energies)
                    for i in range(N_POKEMON):
                        if mask & (1 << i):
                            new_energies[i] -= 1
                    battle_cost = difficulty / POWER_SUM_FOR_MASK[mask]
                    new_idx = encode(new_energies)
                    total = cost_so_far + battle_cost
                    if total < new_dp[new_idx]:
                        new_dp[new_idx] = total
        dp = new_dp

    best = INF
    for idx, cost in enumerate(dp):
        if cost == INF:
            continue
        energies = decode(idx)
        if any(e >= 1 for e in energies):
            best = min(best, cost)

    return best


if __name__ == "__main__":
    import time

    t0 = time.time()
    result = solve_exact()
    t1 = time.time()
    print("Custo otimo exato (Tarefa 1):", round(result, 4))
    print("Tempo:", round(t1 - t0, 2), "s")
