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
                electrical_comp = self.entity.game_state.current_level.tilemap.get_electrical(wire_pos[0], wire_pos[1])
                if electrical_comp:
                    # Only mark as completed if task progress is complete
                    task_comp = self.entity.get_component('task')
                    if task_comp and task_comp.current_task and task_comp.current_task.progress >= task_comp.current_task.work_time:
                        electrical_comp.under_construction = False  # Mark as completed
                        print(f"[DEBUG] Wire at {wire_pos} marked as completed")
                        # Clear the task only after successful completion
                        self.wire_task = None
                        # Notify task system of completion
                        self.entity.game_state.task_system.complete_task(task_comp.current_task)
                        task_comp.stop()
            except AttributeError as e:
                print(f"Error updating wire: {e}")

    def render(self, surface, camera_x: float, camera_y: float) -> None:
        """Draw wire and its construction state"""
        if not self.wire_task:
            return
        
        zoom = self.entity.game_state.zoom_level
        wire_pos = self.wire_task[0]
        
        # Calculate screen position
        screen_x = (wire_pos[0] * TILE_SIZE - camera_x) * zoom
        screen_y = (wire_pos[1] * TILE_SIZE - camera_y) * zoom
        tile_size = TILE_SIZE * zoom
        
        # Get wire component to check construction state
        electrical_comp = self.entity.game_state.current_level.tilemap.get_electrical(wire_pos[0], wire_pos[1])
        if not electrical_comp:
            return
        
        # Choose color based on construction state
        wire_color = (255, 255, 0) if electrical_comp.under_construction else (0, 255, 255)  # Yellow -> Cyan
        wire_width = max(2 * zoom, 1) if electrical_comp.under_construction else max(3 * zoom, 2)
        
        # Draw main wire line
        pygame.draw.line(surface, wire_color,
                        (screen_x + tile_size * 0.2, screen_y + tile_size * 0.5),
                        (screen_x + tile_size * 0.8, screen_y + tile_size * 0.5),
                        int(wire_width))
        
        # Draw connection nodes
        node_radius = max(3 * zoom, 2)
        pygame.draw.circle(surface, wire_color,
                          (int(screen_x + tile_size * 0.2), int(screen_y + tile_size * 0.5)),
                          int(node_radius))
        pygame.draw.circle(surface, wire_color,
                          (int(screen_x + tile_size * 0.8), int(screen_y + tile_size * 0.5)),
                          int(node_radius)) 