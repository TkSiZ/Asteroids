# ASTEROIDES v2.0
# Constantes de gameplay, renderização e balanceamento.

WIDTH  = 960
HEIGHT = 720
FPS    = 60

START_LIVES     = 3
SAFE_SPAWN_TIME = 2.0
WAVE_DELAY      = 2.0

SHIP_RADIUS       = 15
SHIP_TURN_SPEED   = 220.0
SHIP_THRUST       = 220.0
SHIP_FRICTION     = 0.995
SHIP_FIRE_RATE    = 0.2
SHIP_BULLET_SPEED = 420.0
HYPERSPACE_COST   = 250

AST_VEL_MIN = 30.0
AST_VEL_MAX = 90.0
AST_SIZES = {
    "L": {"r": 46, "score": 20,  "split": ["M", "M"]},
    "M": {"r": 24, "score": 50,  "split": ["S", "S"]},
    "S": {"r": 12, "score": 100, "split": []},
}

# Variantes de asteroide
EXPLOSIVE_CHANCE = 0.15
FROZEN_CHANCE    = 0.10
SPREAD_CHANCE    = 0.10
TIME_CHANCE      = 0.10

EXPLOSIVE_RADIUS = 80
FROZEN_DURATION  = 1.5
SPREAD_DUR       = 10.0
SPREAD_ANGLE     = 15.0
FREEZE_DUR  = 5.0

BULLET_RADIUS = 2
BULLET_TTL    = 1.0
MAX_BULLETS   = 12

UFO_SPAWN_EVERY  = 15.0
UFO_SPEED        = 80.0
UFO_FIRE_EVERY   = 1.2
UFO_BULLET_SPEED = 260.0
UFO_BULLET_TTL   = 1.8
UFO_BIG   = {"r": 18, "score": 200,  "aim": 0.2}
UFO_SMALL = {"r": 12, "score": 1000, "aim": 0.6}

# Escudo
SHIELD_DURATION        = 3.0
SHIELD_COOLDOWN        = 8.0
SHIELD_ENERGY_PER_KILL = 30
SHIELD_ENERGY_MAX      = 100

# Combo
COMBO_WINDOW = 1.5
COMBO_MAX    = 6

# Partida
MATCH_DURATION = 120.0

# Cores
WHITE  = (240, 240, 240)
GRAY   = (120, 120, 120)
BLACK  = (0,   0,   0)
RED    = (220, 60,  60)
YELLOW = (240, 210, 50)
CYAN   = (60,  220, 220)
GREEN  = (60,  220, 100)
ORANGE = (240, 140, 40)
PURPLE = (200, 100, 255)

RANDOM_SEED = None
