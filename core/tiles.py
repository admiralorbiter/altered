from dataclasses import dataclass
from typing import Tuple

@dataclass
class Tile:
    id: int
    name: str
    color: Tuple[int, int, int]
    walkable: bool = True
    description: str = ""
    
# Define tile constants
TILE_FLOOR = Tile(
    id=0,
    name="floor",
    color=(100, 100, 100),
    walkable=True,
    description="Basic floor tile"
)

TILE_GRASS = Tile(
    id=1,
    name="grass",
    color=(50, 200, 50),
    walkable=True,
    description="Grassy terrain"
)

TILE_ROCK = Tile(
    id=2,
    name="rock",
    color=(160, 82, 45),
    walkable=False,
    description="Rocky obstacle"
)

TILE_WALL = Tile(
    id=3,
    name="wall",
    color=(80, 80, 80),
    walkable=False,
    description="Basic wall"
)

TILE_BARRIER = Tile(
    id=4,
    name="barrier",
    color=(139, 0, 0),
    walkable=False,
    description="Energy barrier"
)

# Dictionary for easy lookup
TILES = {
    "floor": TILE_FLOOR,
    "grass": TILE_GRASS,
    "rock": TILE_ROCK,
    "wall": TILE_WALL,
    "barrier": TILE_BARRIER
}

# Dictionary for ID lookup
TILES_BY_ID = {tile.id: tile for tile in TILES.values()} 