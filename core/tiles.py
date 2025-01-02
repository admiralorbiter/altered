from dataclasses import dataclass, field
from typing import Tuple, List

@dataclass
class ElectricalComponent:
    """
    Represents an electrical component in the power grid system.
    Components can be wires, power sources, or consumers, each with their own
    power handling characteristics and connection states.
    """
    type: str  # 'wire', 'source', 'consumer'
    _under_construction: bool = True  # Use private field for property
    _is_built: bool = False  # Use private field for property
    capacity: float = 0.0
    current_power: float = 0.0
    connected_tiles: List[Tuple[int, int]] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize after dataclass fields are set"""
        print(f"[DEBUG] Creating new ElectricalComponent:")
        print(f"  - type: {self.type}")
        print(f"  - under_construction: {self._under_construction}")
        print(f"  - is_built: {self._is_built}")
    
    @property
    def under_construction(self):
        return self._under_construction
        
    @under_construction.setter
    def under_construction(self, value):
        self._under_construction = value
        print(f"[DEBUG] ElectricalComponent under_construction set to {value}")
        
    @property
    def is_built(self):
        return self._is_built
        
    @is_built.setter
    def is_built(self, value):
        self._is_built = value
        print(f"[DEBUG] ElectricalComponent is_built set to {value}")
    

@dataclass
class Tile:
    """
    Represents a basic terrain tile with properties that affect gameplay mechanics.
    Each tile type has unique characteristics like walkability and appearance.
    """
    id: int  # Unique identifier for the tile type
    name: str  # Human-readable name
    color: Tuple[int, int, int]  # RGB color for rendering
    walkable: bool = True  # Whether entities can move through this tile
    description: str = ""  # Descriptive text for UI/tooltips
    
# Terrain Tiles
# These represent the basic building blocks of the game world

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

# Electrical Infrastructure Tiles
# These tiles represent various components of the power distribution system

TILE_WIRE = Tile(
    id=10,
    name="wire",
    color=(255, 255, 0),  # Yellow for high visibility
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