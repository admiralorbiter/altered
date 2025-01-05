from components.base_component import Component
from utils.config import TILE_SIZE

class LifeSupportComponent(Component):
    def __init__(self, entity):
        super().__init__(entity)
        self.type = 'life_support'
        self._under_construction = True
        self._is_built = False
        self.construction_time = 4.0  # Slightly faster than reactor
        self.construction_progress = 0.0
        self.size = (2, 2)  # 2x2 tiles like reactor
        self.connected_tiles = []
        self.connection_points = []
        self.occupied_tiles = []  # Track all tiles this life support occupies
        
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
        
        # Life support specific properties
        self.oxygen_generation_rate = 10.0  # Amount of oxygen generated per second
        self.power_consumption = 5.0  # Power needed from reactor
        self.is_powered = False
        self.is_active = False  # Whether it's currently generating oxygen
        self.power_required = 2.0  # Each life support needs 2 power
        
        # Register with power system
        if self.entity and self.entity.game_state:
            self.entity.game_state.power_system.register_power_consumer(self, self.power_required)

    def cleanup(self):
        """Called when component is removed/destroyed"""
        # Restore walkability when component is removed
        if self.entity and self.entity.game_state:
            tilemap = self.entity.game_state.current_level.tilemap
            for x, y in self.occupied_tiles:
                tilemap.set_walkable(x, y, True)

    @property
    def under_construction(self) -> bool:
        return self._under_construction

    @property
    def is_built(self) -> bool:
        return self._is_built

    def update(self, dt: float) -> None:
        if self.under_construction:
            self.construction_progress += dt
            if self.construction_progress >= self.construction_time:
                self._under_construction = False
                self._is_built = True
                
        elif self.is_built and self.is_powered:
            # Generate oxygen when powered
            if self.entity.game_state and hasattr(self.entity.game_state, 'oxygen_system'):
                # Add oxygen to each tile around the life support
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        x = self.primary_tile[0] + dx
                        y = self.primary_tile[1] + dy
                        self.entity.game_state.oxygen_system.add_oxygen(
                            x, y, 
                            self.oxygen_generation_rate * dt / 25.0  # Distribute over area
                        )
                self.is_active = True
        else:
            self.is_active = False

    def set_power_state(self, is_powered: bool) -> None:
        """Update whether the life support system is receiving power"""
        self.is_powered = is_powered 