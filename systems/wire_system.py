import pygame
from entities.base_entity import Entity
from entities.cat import CatState
from utils.config import *
from core.tiles import ElectricalComponent
from dataclasses import dataclass
from typing import Optional, Tuple, List
from enum import Enum

class TaskType(Enum):
    WIRE_CONSTRUCTION = "wire_construction"
    # Future task types can be added here

@dataclass
class Task:
    type: TaskType
    position: Tuple[int, int]
    assigned_to: Optional[Entity] = None
    priority: int = 1
    completed: bool = False


class WireSystem:
    def __init__(self, game_state):
        self.game_state = game_state
        self.is_placing_wire = False
        self.ghost_position = None
        self.ghost_valid = False
        self.pending_wires = []
        self.start_position = None
        self.current_wire_path = []

    def handle_event(self, event):
        if not self.game_state.wire_mode:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            print("DEBUG: Starting wire placement")
            self.is_placing_wire = True
            self._update_ghost_position(event.pos)
            self.start_position = self.ghost_position
            return True
            
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            print(f"DEBUG: Ending wire placement. Start: {self.start_position}, End: {self.ghost_position}")
            if self.start_position and self.ghost_position:
                positions = self._get_line_positions(
                    self.start_position[0], self.start_position[1],
                    self.ghost_position[0], self.ghost_position[1]
                )
                self.current_wire_path = [
                    pos for pos in positions 
                    if self._is_valid_wire_position(pos[0], pos[1])
                ]
                print(f"DEBUG: Wire path: {self.current_wire_path}")
                self._place_wire_path()
            
            self.is_placing_wire = False
            self.start_position = None
            self.current_wire_path = []
            return True
            
        elif event.type == pygame.MOUSEMOTION and self.is_placing_wire:
            self._update_ghost_position(event.pos)
            return True
        
        return False

    def _update_ghost_position(self, mouse_pos):
        tile_x = int((mouse_pos[0] / self.game_state.zoom_level + self.game_state.camera_x) // TILE_SIZE)
        tile_y = int((mouse_pos[1] / self.game_state.zoom_level + self.game_state.camera_y) // TILE_SIZE)
        self.ghost_position = (tile_x, tile_y)
        self.ghost_valid = self._is_valid_wire_position(tile_x, tile_y)

    def _get_line_positions(self, x1, y1, x2, y2):
        positions = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        
        if dx > dy:
            err = dx / 2.0
            while x != x2:
                positions.append((x, y))
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y2:
                positions.append((x, y))
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
                
        positions.append((x2, y2))
        return positions

    def _place_wire_path(self):
        print("\n=== DEBUG: Wire Path Placement ===")
        print(f"Wire mode: {self.game_state.wire_mode}")
        print(f"Current wire path: {self.current_wire_path}")
        
        for pos in self.current_wire_path:
            print(f"\nCreating wire task at position: {pos}")
            # Add to pending wires first
            self.pending_wires.append(pos)
            
            # Create the task
            task = self.game_state.task_system.add_task(
                TaskType.WIRE_CONSTRUCTION,
                pos,
                priority=1
            )
            print(f"Created task: {task}")
        
        # Try to assign the pending wires immediately
        self._assign_wire_placement()

    def _assign_wire_placement(self):
        print("\n=== DEBUG: Wire Assignment ===")
        print(f"Pending wires: {self.pending_wires}")
        print(f"Available tasks: {[t.position for t in self.game_state.task_system.available_tasks]}")
        
        if not self.pending_wires:
            print("No pending wires to assign")
            return

        print(f"\n=== Starting Wire Assignments ===")
        print(f"Pending wires: {self.pending_wires}")
        wire_assignments = {}
        
        for wire_pos in self.pending_wires[:]:  # Create a copy to iterate
            nearest_entity = self._find_nearest_entity(wire_pos)
            print(f"Found nearest entity for wire at {wire_pos}: {id(nearest_entity) if nearest_entity else None}")
            if nearest_entity:
                # Get the task for this position
                task = next((t for t in self.game_state.task_system.available_tasks 
                            if t.position == wire_pos), None)
                if task:
                    print(f"Assigning task at {wire_pos} to entity {id(nearest_entity)}")
                    task.assigned_to = nearest_entity
                    nearest_entity.current_task = task
                    nearest_entity.set_wire_task(wire_pos, 'wire')
                    self.pending_wires.remove(wire_pos)
                    # Force state change to WORKING
                    nearest_entity._switch_state(CatState.WORKING)

    def _find_nearest_entity(self, wire_pos):
        nearest_entity = None
        min_distance = float('inf')
        
        selected_alien = next((alien for alien in self.game_state.current_level.aliens 
                             if alien.selected), None)
        if selected_alien:
            distance = self._calculate_distance(selected_alien, wire_pos)
            if distance < min_distance:
                nearest_entity = selected_alien
                min_distance = distance

        for cat in self.game_state.current_level.cats:
            if not cat.is_dead and not cat.current_task:
                distance = self._calculate_distance(cat, wire_pos)
                if distance < min_distance:
                    nearest_entity = cat
                    min_distance = distance

        return nearest_entity

    def _calculate_distance(self, entity, wire_pos):
        return ((entity.position.x // TILE_SIZE - wire_pos[0]) ** 2 + 
                (entity.position.y // TILE_SIZE - wire_pos[1]) ** 2) ** 0.5 

    def _is_valid_wire_position(self, x, y):
        if not (0 <= x < self.game_state.current_level.tilemap.width and 
                0 <= y < self.game_state.current_level.tilemap.height):
            return False
        
        if (x, y) in self.game_state.current_level.tilemap.electrical_components:
            return False
        
        return True 

    def draw(self, surface):
        # First draw all pending/under construction wires
        for pos in self.pending_wires:
            screen_x = (pos[0] * TILE_SIZE - self.game_state.camera_x) * self.game_state.zoom_level
            screen_y = (pos[1] * TILE_SIZE - self.game_state.camera_y) * self.game_state.zoom_level
            tile_size = TILE_SIZE * self.game_state.zoom_level
            
            # Draw under construction wire in yellow
            wire_color = (255, 255, 0)  # Yellow for under construction
            wire_width = max(2 * self.game_state.zoom_level, 1)
            
            # Draw the wire line
            pygame.draw.line(surface, wire_color,
                            (screen_x + tile_size * 0.2, screen_y + tile_size * 0.5),
                            (screen_x + tile_size * 0.8, screen_y + tile_size * 0.5),
                            int(wire_width))
            
            # Draw connection nodes
            node_radius = max(2 * self.game_state.zoom_level, 1)
            pygame.draw.circle(surface, wire_color,
                             (int(screen_x + tile_size * 0.2), int(screen_y + tile_size * 0.5)),
                             int(node_radius))
            pygame.draw.circle(surface, wire_color,
                             (int(screen_x + tile_size * 0.8), int(screen_y + tile_size * 0.5)),
                             int(node_radius))

        # Then draw all completed wires
        for pos, component in self.game_state.current_level.tilemap.electrical_components.items():
            if component.type != 'wire':
                continue
            
            screen_x = (pos[0] * TILE_SIZE - self.game_state.camera_x) * self.game_state.zoom_level
            screen_y = (pos[1] * TILE_SIZE - self.game_state.camera_y) * self.game_state.zoom_level
            tile_size = TILE_SIZE * self.game_state.zoom_level
            
            # Draw completed wire in cyan
            wire_color = (0, 255, 255)  # Cyan for completed
            wire_width = max(4 * self.game_state.zoom_level, 2)
            
            # Draw the wire line
            pygame.draw.line(surface, wire_color,
                            (screen_x + tile_size * 0.2, screen_y + tile_size * 0.5),
                            (screen_x + tile_size * 0.8, screen_y + tile_size * 0.5),
                            int(wire_width))
            
            # Draw connection nodes
            node_radius = max(3 * self.game_state.zoom_level, 2)
            pygame.draw.circle(surface, wire_color,
                             (int(screen_x + tile_size * 0.2), int(screen_y + tile_size * 0.5)),
                             int(node_radius))
            pygame.draw.circle(surface, wire_color,
                             (int(screen_x + tile_size * 0.8), int(screen_y + tile_size * 0.5)),
                             int(node_radius))

        # Finally draw the ghost wire preview if placing
        if self.game_state.wire_mode and self.is_placing_wire and self.start_position and self.ghost_position:
            # Get all positions in the line
            positions = self._get_line_positions(
                self.start_position[0], self.start_position[1],
                self.ghost_position[0], self.ghost_position[1]
            )
            
            # Draw each position in the ghost line
            for pos in positions:
                if not self._is_valid_wire_position(pos[0], pos[1]):
                    continue
                
                screen_x = (pos[0] * TILE_SIZE - self.game_state.camera_x) * self.game_state.zoom_level
                screen_y = (pos[1] * TILE_SIZE - self.game_state.camera_y) * self.game_state.zoom_level
                tile_size = TILE_SIZE * self.game_state.zoom_level
                
                # Draw ghost wire in semi-transparent white
                wire_color = (255, 255, 255, 128)
                wire_width = max(2 * self.game_state.zoom_level, 1)
                
                # Draw the ghost wire line
                pygame.draw.line(surface, wire_color,
                               (screen_x + tile_size * 0.2, screen_y + tile_size * 0.5),
                               (screen_x + tile_size * 0.8, screen_y + tile_size * 0.5),
                               int(wire_width))
                
                # Draw ghost connection nodes
                node_radius = max(2 * self.game_state.zoom_level, 1)
                pygame.draw.circle(surface, wire_color,
                                (int(screen_x + tile_size * 0.2), int(screen_y + tile_size * 0.5)),
                                int(node_radius))
                pygame.draw.circle(surface, wire_color,
                                (int(screen_x + tile_size * 0.8), int(screen_y + tile_size * 0.5)),
                                int(node_radius))

    def complete_wire_construction(self, position):
        """Called when a cat completes wire construction at a position"""
        print(f"\n=== DEBUG: Completing Wire Construction ===")
        print(f"Position: {position}")
        print(f"Current electrical components: {self.game_state.current_level.tilemap.electrical_components}")
        
        # Create and configure the wire component
        component = ElectricalComponent(type='wire', under_construction=False)
        
        # Add to tilemap's data structures
        self.game_state.current_level.tilemap.electrical_components[position] = component
        self.game_state.current_level.tilemap.electrical_layer[position[1]][position[0]] = component
        
        # Debug: Verify component was added
        print(f"Added to electrical_components: {position in self.game_state.current_level.tilemap.electrical_components}")
        print(f"Component at position: {self.game_state.current_level.tilemap.electrical_components.get(position)}")
        print(f"Component type: {type(self.game_state.current_level.tilemap.electrical_components.get(position))}")
        print(f"Added to electrical_layer: {self.game_state.current_level.tilemap.electrical_layer[position[1]][position[0]] is not None}")
        print(f"Updated electrical components: {self.game_state.current_level.tilemap.electrical_components}")
        
        # Remove from pending wires
        if position in self.pending_wires:
            self.pending_wires.remove(position)
            print(f"Removed from pending wires. Remaining: {self.pending_wires}")