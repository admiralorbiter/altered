from components.base_component import Component
from components.pathfinding_component import PathfindingComponent
from utils.config import TILE_SIZE
import pygame

class WireComponent(Component):
    def __init__(self, entity):
        super().__init__(entity)
        self.wire_task = None  # (wire_pos, wire_type)
        self._pathfinding = None

    def start(self) -> None:
        """Get reference to pathfinding component when starting"""
        self._pathfinding = self.entity.get_component(PathfindingComponent)

    def set_wire_task(self, wire_pos, wire_type) -> bool:
        """Set a wire placement task and path to it"""
        if not self._pathfinding:
            return False

        # Store the wire task
        self.wire_task = (wire_pos, wire_type)
        
        # Use pathfinding to get to wire location
        result = self._pathfinding.set_target(wire_pos[0], wire_pos[1])
        return result

    def update(self, dt: float) -> None:
        """Check if we've reached wire placement location"""
        if not self.wire_task:
            return

        # If pathfinding is complete and we're not moving
        if not self._pathfinding.path and not self.entity.get_component('movement').moving:
            wire_pos, wire_type = self.wire_task
            # Place the wire
            try:
                self.entity.game_state.current_level.tilemap.set_electrical(
                    wire_pos[0], wire_pos[1], wire_type
                )
            except AttributeError as e:
                print(f"Error placing wire: {e}")
            
            # Clear the task
            self.wire_task = None

    def render(self, surface, camera_x: float, camera_y: float) -> None:
        """Draw wire task indicator"""
        if self.wire_task:
            zoom = getattr(self.entity.game_state, 'zoom_level', 1)
            wire_pos = self.wire_task[0]
            # Draw indicator at wire placement location
            screen_x = (wire_pos[0] * TILE_SIZE + TILE_SIZE//2 - camera_x) * zoom
            screen_y = (wire_pos[1] * TILE_SIZE + TILE_SIZE//2 - camera_y) * zoom
            pygame.draw.circle(surface, (0, 255, 255), 
                             (int(screen_x), int(screen_y)), 
                             int(5 * zoom)) 