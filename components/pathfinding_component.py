from components.base_component import Component
from components.movement_component import MovementComponent
from utils.pathfinding import find_path
from utils.config import TILE_SIZE
import pygame

class PathfindingComponent(Component):
    def __init__(self, entity):
        super().__init__(entity)
        self.path = None
        self.current_waypoint = 0
        self._movement = None
        self.tile_size = TILE_SIZE  # Use the global tile size

    def start(self) -> None:
        """Get reference to movement component when starting"""
        self._movement = self.entity.get_component(MovementComponent)

    def set_target(self, tile_x: int, tile_y: int) -> bool:
        """Set path to target tile using A* pathfinding"""
        
        if not self._movement:
            return False

        # Get current tile position
        current_tile = (
            int(self.entity.position.x // self.tile_size),
            int(self.entity.position.y // self.tile_size)
        )
        target_tile = (tile_x, tile_y)

        # Get tilemap from game state
        try:
            tilemap = self.entity.game_state.current_level.tilemap
        except AttributeError as e:
            return False

        # Find path using A*
        self.path = find_path(
            current_tile, 
            target_tile,
            tilemap,
            self.entity.game_state,
            self.entity
        )

        if self.path:
            self.current_waypoint = 0
            self._set_next_waypoint()
            return True
        return False

    def _set_next_waypoint(self) -> None:
        """Update movement component with next waypoint"""
        if not self.path or not self._movement:
            return

        next_tile = self.path[self.current_waypoint]
        # Convert tile coordinates to pixel coordinates (center of tile)
        pixel_x = next_tile[0] * self.tile_size + (self.tile_size // 2)
        pixel_y = next_tile[1] * self.tile_size + (self.tile_size // 2)
        self._movement.set_target_position(float(pixel_x), float(pixel_y))

    def update(self, dt: float) -> None:
        """Check if current waypoint reached and set next one"""
        if not self.path or not self._movement:
            return

        # Check if we've reached the current waypoint
        if not self._movement.moving and self.current_waypoint < len(self.path) - 1:
            # Move to next waypoint
            self.current_waypoint += 1
            self._set_next_waypoint()
        elif not self._movement.moving:
            # Path completed
            self.path = None

    def render(self, surface, camera_x: float, camera_y: float) -> None:
        """Draw the path for debugging"""
        if self.path and len(self.path) > self.current_waypoint:
            zoom = self.entity.game_state.zoom_level
            # Draw lines between waypoints
            for i in range(self.current_waypoint, len(self.path) - 1):
                start_pos = (
                    self.path[i][0] * self.tile_size + self.tile_size // 2,
                    self.path[i][1] * self.tile_size + self.tile_size // 2
                )
                end_pos = (
                    self.path[i + 1][0] * self.tile_size + self.tile_size // 2,
                    self.path[i + 1][1] * self.tile_size + self.tile_size // 2
                )
                pygame.draw.line(surface, (0, 255, 0), 
                               ((start_pos[0] - camera_x) * zoom, 
                                (start_pos[1] - camera_y) * zoom),
                               ((end_pos[0] - camera_x) * zoom, 
                                (end_pos[1] - camera_y) * zoom), 2) 