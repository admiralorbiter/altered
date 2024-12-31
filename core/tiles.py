from dataclasses import dataclass, field
from typing import Tuple, List

@dataclass
class ElectricalComponent:
    type: str  # 'wire', 'source', 'consumer'
    capacity: float = 0.0  # Power capacity
    current_power: float = 0.0
    connected_tiles: List[Tuple[int, int]] = field(default_factory=list)
    under_construction: bool = True  # This stays True forever

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

TILE_WIRE = Tile(
    id=10,
    name="wire",
    color=(255, 255, 0),  # Yellow for visibility
    walkable=True,
    description="Basic electrical wire"
)

TILE_POWER_SOURCE = Tile(
    id=11,
    name="power_source",
    color=(0, 255, 0),  # Green for power
    walkable=True,
    description="Power generator"
)

TILE_POWER_CONSUMER = Tile(
    id=12,
    name="power_consumer",
    color=(255, 0, 0),  # Red for consumer
    walkable=True,
    description="Power consumer"
)

# Dictionary for easy lookup
TILES = {
    "floor": TILE_FLOOR,
    "grass": TILE_GRASS,
    "rock": TILE_ROCK,
    "wall": TILE_WALL,
    "barrier": TILE_BARRIER,
    "wire": TILE_WIRE,
    "power_source": TILE_POWER_SOURCE,
    "power_consumer": TILE_POWER_CONSUMER
}

# Dictionary for ID lookup
TILES_BY_ID = {tile.id: tile for tile in TILES.values()} 