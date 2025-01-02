import pygame
from components.base_entity import Entity
from utils.types import TaskType, Task
from utils.config import *
from core.tiles import ElectricalComponent
from dataclasses import dataclass
from typing import Optional, Tuple, List
from enum import Enum

class TaskType(Enum):
    """Enumeration of different task types in the game"""
    WIRE_CONSTRUCTION = "wire_construction"
    # Future task types can be added here

@dataclass
class Task:
    """Represents a game task that can be assigned to entities"""
    type: TaskType
    position: Tuple[int, int]
    assigned_to: Optional[Entity] = None
    priority: int = 1  # 0 = low, 1 = normal, 2 = high, 3 = critical
    completed: bool = False
    
    def should_interrupt(self) -> bool:
        """
        Determines if this task should interrupt an entity's current activity
        Returns:
            bool: True if priority is high or critical (>= 2)
        """
        return self.priority >= 2


class WireSystem:
    """
    Manages the wire placement, construction, and rendering system in the game.
    Handles user interactions for wire placement and maintains wire state.
    """
    def __init__(self, game_state):
        """
        Initialize the wire system
        Args:
            game_state: Reference to the main game state
        """
        self.game_state = game_state
        self.is_placing_wire = False
        self.ghost_position = None
        self.ghost_valid = False
        self.start_position = None
        self.current_wire_path = []
        self.construction_progress = {}  # Track progress per wire position
        
    def handle_event(self, event):
        """
        Handle pygame events related to wire placement
        Args:
            event: Pygame event to process
        Returns:
            bool: True if event was handled by wire system
        """
        if not self.game_state.wire_mode:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.is_placing_wire = True
            self._update_ghost_position(event.pos)
            self.start_position = self.ghost_position
            return True
            
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.start_position and self.ghost_position:
                positions = self._get_line_positions(
                    self.start_position[0], self.start_position[1],
                    self.ghost_position[0], self.ghost_position[1]
                )
                self.current_wire_path = [
                    pos for pos in positions 
                    if self._is_valid_wire_position(pos[0], pos[1])
                ]
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
        """
        Updates the ghost wire position based on mouse coordinates
        Args:
            mouse_pos: Tuple of (x, y) mouse position in screen coordinates
        """
        tile_x = int((mouse_pos[0] / self.game_state.zoom_level + self.game_state.camera_x) // TILE_SIZE)
        tile_y = int((mouse_pos[1] / self.game_state.zoom_level + self.game_state.camera_y) // TILE_SIZE)
        self.ghost_position = (tile_x, tile_y)
        self.ghost_valid = self._is_valid_wire_position(tile_x, tile_y)

    def _get_line_positions(self, x1, y1, x2, y2):
        """
        Implements Bresenham's line algorithm to get all tile positions between two points
        Args:
            x1, y1: Starting point coordinates
            x2, y2: Ending point coordinates
        Returns:
            List[Tuple[int, int]]: List of tile positions along the line
        """
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
        """
        Places a path of wires and creates construction tasks for each wire
        End points of the wire path are given higher priority
        Returns:
            List[Task]: List of created construction tasks
        """
        created_tasks = []
        for i, pos in enumerate(self.current_wire_path):
            # Create electrical component with explicit state
            component = ElectricalComponent(
                type='wire',
                under_construction=True,
                is_built=False  # Explicitly set initial state
            )
            
            # Place component in tilemap with verification
            success = self.game_state.current_level.tilemap.set_electrical(pos[0], pos[1], component)
            if success:
                # Verify component was placed correctly
                placed_component = self.game_state.current_level.tilemap.get_electrical(pos[0], pos[1])
                if not placed_component or placed_component.type != 'wire':
                    print(f"[DEBUG] ERROR: Wire placement verification failed at {pos}")
                    continue
                    
                priority = 2 if i == 0 or i == len(self.current_wire_path) - 1 else 1
                task = self.game_state.task_system.add_task(
                    TaskType.WIRE_CONSTRUCTION,
                    pos,
                    priority=priority
                )
                created_tasks.append(task)
                print(f"[DEBUG] Created wire construction task at {pos}")
                print(f"  - Component state: under_construction={placed_component.under_construction}, is_built={placed_component.is_built}")
        
        return created_tasks

    def complete_wire_construction(self, position):
        """Marks a wire as constructed at the given position"""
        print(f"\n[DEBUG] ===== Wire Construction Completion =====")
        print(f"[DEBUG] Attempting to complete wire at {position}")
        
        tilemap = self.game_state.current_level.tilemap
        component = tilemap.get_electrical(position[0], position[1])
        
        if not component:
            print(f"[DEBUG] ERROR: No electrical component found at {position}")
            return False
            
        # Force state update with verification
        try:
            # Update component state
            component.under_construction = False
            component.is_built = True
            
            # Verify state change
            if not component.is_built or component.under_construction:
                raise ValueError("State change failed")
                
            # Update connected components
            self._update_wire_connections(position)
            
            # Force tilemap update and ensure it's properly saved
            tilemap.electrical_components[position] = component
            
            # Clear construction progress
            if position in self.construction_progress:
                del self.construction_progress[position]
                
            print(f"[DEBUG] Wire construction completed successfully at {position}")
            print(f"[DEBUG] Component state: is_built={component.is_built}, under_construction={component.under_construction}")
            return True
            
        except Exception as e:
            print(f"[DEBUG] ERROR during wire completion: {str(e)}")
            return False
            
    def update_construction_progress(self, position, dt):
        """Update construction progress for a specific wire"""
        if position not in self.construction_progress:
            self.construction_progress[position] = 0.0
            print(f"[DEBUG] Starting new wire construction at {position}")
        
        # Use fixed increment to avoid floating point issues
        increment = dt * 0.75  # Slightly faster progress
        current_progress = self.construction_progress[position]
        new_progress = min(current_progress + increment, 2.0)  # Cap at 2.0
        self.construction_progress[position] = new_progress
        
        # Only log every 0.1 progress
        if int(new_progress * 10) != int(current_progress * 10):
            print(f"[DEBUG] Wire progress at {position}: {new_progress:.1f}/2.0")
        
        # Check for completion with some tolerance
        if new_progress >= 1.99:  # Allow for floating point imprecision
            success = self.complete_wire_construction(position)
            if success:
                print(f"[DEBUG] Wire construction completed at {position}")
                return True
            
        return False

    def _update_wire_connections(self, position):
        """Update wire connections after construction"""
        x, y = position
        tilemap = self.game_state.current_level.tilemap
        
        # Check adjacent tiles for other wires
        adjacent = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        for adj_pos in adjacent:
            adj_comp = tilemap.get_electrical(adj_pos[0], adj_pos[1])
            if adj_comp and adj_comp.is_built:  # Only connect to built wires
                # Add mutual connections if they don't exist
                if position not in adj_comp.connected_tiles:
                    adj_comp.connected_tiles.append(position)
                if adj_pos not in tilemap.electrical_components[position].connected_tiles:
                    tilemap.electrical_components[position].connected_tiles.append(adj_pos)

    def draw(self, surface):
        """
        Renders all wires and ghost wire previews to the screen
        Args:
            surface: Pygame surface to draw on
        """
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
        """
        Checks if a wire can be placed at the given coordinates
        Args:
            x, y: Coordinates to check
        Returns:
            bool: True if position is valid for wire placement
        """
        if not (0 <= x < self.game_state.current_level.tilemap.width and 
                0 <= y < self.game_state.current_level.tilemap.height):
            return False
        
        if (x, y) in self.game_state.current_level.tilemap.electrical_components:
            return False
        
        return True 