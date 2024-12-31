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
        """Place a path of wires and create tasks for their construction"""
        print("\n=== Starting Wire Path Placement ===")
        print(f"Path length: {len(self.current_wire_path)}")
        
        for pos in self.current_wire_path:
            # Create wire component marked as under construction
            component = ElectricalComponent(
                type='wire',
                under_construction=True
            )
            
            # Add the component to the tilemap - this is our single source of truth
            success = self.game_state.current_level.tilemap.set_electrical(pos[0], pos[1], component)
            if success:
                # Create the task
                task = self.game_state.task_system.add_task(
                    TaskType.WIRE_CONSTRUCTION,
                    pos,
                    priority=1
                )
                print(f"Created wire task at: {pos}")
            else:
                print(f"Failed to place wire at {pos}")

    def complete_wire_construction(self, position):
        """Called when a cat completes wire construction at a position"""
        print("\n=== WIRE CONSTRUCTION DEBUG ===")
        print(f"Attempting to complete wire at: {position}")
        
        # Get the component from tilemap - our single source of truth
        tilemap = self.game_state.current_level.tilemap
        component = tilemap.electrical_components.get(position)
        
        if not component:
            print(f"No component found at {position}")
            return False
            
        if not component.under_construction:
            print(f"Wire at {position} is already completed")
            return False
        
        # Update the component's state
        print(f"Completing wire at {position}")
        component.under_construction = False
        return True

    def draw(self, surface):
        """Draw all wires based solely on their state in the tilemap"""
        tilemap = self.game_state.current_level.tilemap
        
        # Draw all wires based on their construction state
        for pos, comp in tilemap.electrical_components.items():
            if comp.type == 'wire':
                screen_x = (pos[0] * TILE_SIZE - self.game_state.camera_x) * self.game_state.zoom_level
                screen_y = (pos[1] * TILE_SIZE - self.game_state.camera_y) * self.game_state.zoom_level
                tile_size = TILE_SIZE * self.game_state.zoom_level
                
                # Color based on construction state
                wire_color = (255, 255, 0) if comp.under_construction else (0, 255, 255)
                wire_width = max(2 * self.game_state.zoom_level, 1)
                
                pygame.draw.line(surface, wire_color,
                               (screen_x + tile_size * 0.2, screen_y + tile_size * 0.5),
                               (screen_x + tile_size * 0.8, screen_y + tile_size * 0.5),
                               int(wire_width))

        # Draw the ghost wire preview if placing
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

    def _is_valid_wire_position(self, x, y):
        if not (0 <= x < self.game_state.current_level.tilemap.width and 
                0 <= y < self.game_state.current_level.tilemap.height):
            return False
        
        if (x, y) in self.game_state.current_level.tilemap.electrical_components:
            return False
        
        return True 