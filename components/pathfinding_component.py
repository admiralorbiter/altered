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
        print(f"\nPATHFINDING START DEBUG:")
        print(f"Movement component found: {self._movement is not None}")

    def set_target(self, tile_x: int, tile_y: int) -> bool:
        """Set path to target tile using A* pathfinding"""
        print(f"\nPATHFINDING SET_TARGET DEBUG:")
        print(f"Game state exists: {self.entity.game_state is not None}")
        print(f"Movement component exists: {self._movement is not None}")
        
        if not self._movement:
            print("ERROR: No movement component found!")
            return False

        # Get current tile position
        current_tile = (
            int(self.entity.position.x // self.tile_size),
            int(self.entity.position.y // self.tile_size)
        )
        target_tile = (tile_x, tile_y)
        print(f"Current position (pixels): {self.entity.position}")
        print(f"Current tile: {current_tile}")
        print(f"Target tile: {target_tile}")
        print(f"Tile size: {self.tile_size}")

        # Get tilemap from game state
        try:
            tilemap = self.entity.game_state.current_level.tilemap
            print("Successfully got tilemap")
        except AttributeError as e:
            print(f"ERROR getting tilemap: {e}")
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
            print(f"Setting first waypoint at index {self.current_waypoint}")
            self._set_next_waypoint()
            return True
        return False

    def _set_next_waypoint(self) -> None:
        """Update movement component with next waypoint"""
        print(f"\nSETTING WAYPOINT DEBUG:")
        if not self.path or not self._movement:
            print("ERROR: No path or movement component!")
            return

        next_tile = self.path[self.current_waypoint]
        # Convert tile coordinates to pixel coordinates (center of tile)
        pixel_x = (next_tile[0] + 0.5) * self.tile_size
        pixel_y = (next_tile[1] + 0.5) * self.tile_size
        print(f"Next tile: {next_tile}")
        print(f"Target pixel position: ({pixel_x}, {pixel_y})")
        self._movement.set_target_position(pixel_x, pixel_y)

    def update(self, dt: float) -> None:
        """Check if current waypoint reached and set next one"""
        if not self.path or not self._movement:
            return

        # Check if we've reached the current waypoint
        if not self._movement.moving:
            if self.current_waypoint < len(self.path) - 1:
                # Move to next waypoint
                self.current_waypoint += 1
                self._set_next_waypoint()
            else:
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