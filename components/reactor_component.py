from components.base_component import Component
from utils.config import TILE_SIZE

class ReactorComponent(Component):
    def __init__(self, entity):
        super().__init__(entity)
        self.type = 'reactor'  # Set default type
        self._under_construction = True
        self._is_built = False
        self.construction_time = 5.0  # 5 seconds to build
        self.construction_progress = 0.0
        self.size = (2, 2)  # 2x2 tiles
        self.connected_tiles = []  # Add this for wire connections
        self.connection_points = []  # Will store valid connection points
        
    @property
    def is_built(self) -> bool:
        return self._is_built
        
    @property
    def under_construction(self) -> bool:
        return self._under_construction
        
    def update(self, dt: float) -> None:
        if self.under_construction:
            self.construction_progress += dt
            if self.construction_progress >= self.construction_time:
                self._under_construction = False
                self._is_built = True 