from components.base_component import Component
from utils.config import TILE_SIZE

class ReactorComponent(Component):
    def __init__(self, entity):
        super().__init__(entity)
        self.type = 'reactor'
        self._under_construction = True
        self._is_built = False
        self.construction_time = 5.0
        self.construction_progress = 0.0
        self.size = (2, 2)  # 2x2 tiles
        self.connected_tiles = []
        self.connection_points = []
        self.occupied_tiles = []  # Track all tiles this reactor occupies
        self.power_output = 10.0  # Each reactor provides 10 power
        
        # Calculate and store occupied tiles based on position
        base_x = entity.x // TILE_SIZE
        base_y = entity.y // TILE_SIZE
        # Store the primary tile (top-left corner)
        self.primary_tile = (base_x, base_y)
        
        for dx in range(self.size[0]):
            for dy in range(self.size[1]):
                self.occupied_tiles.append((base_x + dx, base_y + dy))
                # Mark tiles as occupied in the tilemap's collision layer
                if self.entity and self.entity.game_state:
                    tilemap = self.entity.game_state.current_level.tilemap
                    tilemap.set_walkable(base_x + dx, base_y + dy, False)
                    
        # Register with power system when built
        if self.entity and self.entity.game_state:
            self.entity.game_state.power_system.register_power_source(self)
        
    def cleanup(self):
        """Called when component is removed/destroyed"""
        # Restore walkability when component is removed
        if self.entity and self.entity.game_state:
            tilemap = self.entity.game_state.current_level.tilemap
            for x, y in self.occupied_tiles:
                tilemap.set_walkable(x, y, True)
        
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
                
                # Mark all occupied tiles as unwalkable in tilemap
                if self.entity and self.entity.game_state:
                    tilemap = self.entity.game_state.current_level.tilemap
                    for tile_pos in self.occupied_tiles:
                        tilemap.set_tile(tile_pos[0], tile_pos[1], 'unwalkable') 
                
                # Register with power system when construction completes
                if self.entity and self.entity.game_state:
                    self.entity.game_state.power_system.register_power_source(self) 