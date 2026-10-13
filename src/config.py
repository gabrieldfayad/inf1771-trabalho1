# Custo (em minutos) para atravessar cada tipo de terreno.
TERRAIN_COST = {
    "M": 200,  # Montanha
    "A": 30,   # Água / mar
    "F": 15,   # Floresta
    "R": 5,    # Rochoso
    ".": 1,    # Livre
}

ORIGIN_CHAR = "1"
DEST_CHAR = "U"
GYM_CHARS = set("23456789BCDEGHIJKLNOPQST")

assert len(GYM_CHARS) == 24

# Origem e destino custam +1 (equivalente a terreno "Livre").
SPECIAL_CHAR_COST = {
    ORIGIN_CHAR: 1,
    DEST_CHAR: 1,
}

GYM_DIFFICULTY = {
    "2": 35, "3": 40, "4": 45, "5": 50, "6": 55, "7": 60, "8": 65, "9": 70,
    "B": 75, "C": 80, "D": 85, "E": 90, "G": 95, "H": 100, "I": 110, "J": 120,
    "K": 130, "L": 140, "N": 150, "O": 155, "P": 160, "Q": 165, "S": 170, "T": 180,
}

assert set(GYM_DIFFICULTY.keys()) == GYM_CHARS

POKEMON_POWER = {
    "Pikachu": 1.5,
    "Bulbassauro": 1.4,
    "Rattata": 1.3,
    "Caterpie": 1.2,
    "Weedle": 1.1,
}

STARTING_ENERGY = 6
