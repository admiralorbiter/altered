import pygame
from components.base_component import Component
from typing import TYPE_CHECKING
from utils.config import TILE_SIZE
from utils.pathfinding import find_path

if TYPE_CHECKING:
    from components.movement_component import MovementComponent

class PathfindingComponent(Component):
    def __init__(self, entity):
        super().__init__(entity)
        self.path = []
        self._movement = None
        self.tile_size = TILE_SIZE
        self.current_waypoint = 0

    def start(self) -> None:
        """Get reference to movement component"""
        from components.movement_component import MovementComponent
        self._movement = self.entity.get_component(MovementComponent)

    def set_target(self, target_x: float, target_y: float) -> bool:
        """Set path to target position using A* pathfinding"""
        if not self._movement or self._movement._force_stop:
            return False

        # Convert pixel coordinates to tile coordinates
        current_tile = (
            int(self.entity.position.x // self.tile_size),
            int(self.entity.position.y // self.tile_size)
        )
        target_tile = (
            int(target_x // self.tile_size),
            int(target_y // self.tile_size)
        )

        # Get tilemap and dimensions
        tilemap = self.entity.game_state.current_level.tilemap
        map_width = tilemap.width
        map_height = tilemap.height

        # Validate tiles are within map bounds
        if (not (0 <= current_tile[0] < map_width and 0 <= current_tile[1] < map_height) or
            not (0 <= target_tile[0] < map_width and 0 <= target_tile[1] < map_height)):
            return False

        # Validate tiles are walkable
        if not tilemap.is_walkable(*current_tile) or not tilemap.is_walkable(*target_tile):
            return False

        # Clear existing path
        self.clear_path()

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

    def waypoint_reached(self) -> None:
        """Called by movement component when waypoint is reached"""
        if self.path and self.current_waypoint < len(self.path) - 1:
            self.current_waypoint += 1
            self._set_next_waypoint()
        else:
            self.path = None
            self.current_waypoint = 0

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

    def clear_path(self) -> None:
        """Clear current path and reset state"""
        if self.path:  # Only clear if there's actually a path
            self.path = []
            self.current_waypoint = 0
            if self._movement:
                self._movement.moving = False
                self._movement.target_position = None

    def can_reach(self, target_x: float, target_y: float) -> bool:
        """Check if a path exists to target position"""
        # Convert pixel coordinates to tile coordinates
        current_tile = (
            int(self.entity.position.x // self.tile_size),
            int(self.entity.position.y // self.tile_size)
        )
        target_tile = (
            int(target_x // self.tile_size),
            int(target_y // self.tile_size)
        )

        # Get tilemap and validate tiles
        tilemap = self.entity.game_state.current_level.tilemap
        if not (0 <= target_tile[0] < tilemap.width and 
                0 <= target_tile[1] < tilemap.height):
            return False

        if not tilemap.is_walkable(*target_tile):
            return False

        # Check if path exists
        path = find_path(
            current_tile,
            target_tile,
            tilemap,
            self.entity.game_state,
            self.entity
        )
        
        return path is not None