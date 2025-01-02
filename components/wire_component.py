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

        wire_pos = self.wire_task[0]
        electrical_comp = self.entity.game_state.current_level.tilemap.get_electrical(wire_pos[0], wire_pos[1])
        
        # If task is complete, clear wire task
        task_comp = self.entity.get_component('task')
        if task_comp and not task_comp.current_task:
            if electrical_comp and electrical_comp.is_built:
                print(f"[WIRE DEBUG] Wire construction completed at {wire_pos}")
                self.wire_task = None
                return
            
        # If pathfinding is complete and we're not moving
        if not self._pathfinding.path and not self.entity.get_component('movement').moving:
            if not task_comp or not task_comp.current_task:
                print(f"[WIRE DEBUG] No active task at {wire_pos}")
                self.wire_task = None