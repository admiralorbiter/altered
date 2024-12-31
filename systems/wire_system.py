import pygame
from utils.config import *
from core.tiles import ElectricalComponent

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
                    if (self._is_valid_wire_position(pos[0], pos[1]))
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
        for pos in self.current_wire_path:
            component = ElectricalComponent(type='wire')
            self.game_state.current_level.tilemap.electrical_components[pos] = component
            self.pending_wires.append(pos)
        self._assign_wire_placement()

    def _assign_wire_placement(self):
        if not self.pending_wires:
            return

        wire_assignments = {}
        
        for wire_pos in self.pending_wires:
            nearest_entity = self._find_nearest_entity(wire_pos)
            if nearest_entity:
                if nearest_entity not in wire_assignments:
                    wire_assignments[nearest_entity] = []
                wire_assignments[nearest_entity].append(wire_pos)

        for entity, positions in wire_assignments.items():
            for wire_pos in positions:
                entity.set_wire_task(wire_pos, 'wire')
                if wire_pos in self.pending_wires:
                    self.pending_wires.remove(wire_pos)

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