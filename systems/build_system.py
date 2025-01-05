import pygame
from components.base_entity import Entity
from components.reactor_component import ReactorComponent
from utils.config import TILE_SIZE
from typing import Dict, Type, Tuple
from components.base_component import Component

class BuildSystem:
    """
    Handles placement and construction of all buildable components.
    Acts as a factory and manager for different building types.
    """
    def __init__(self, game_state):
        self.game_state = game_state
        self.is_placing = False
        self.current_building_type = None
        self.ghost_position = None
        self.ghost_valid = False
        
        # Register different building types and their components
        self.building_types = {
            'reactor': {
                'component_class': ReactorComponent,
                'size': (2, 2),
                'preview_color': (0, 255, 128),
                'walkable': False,
            },
            # Easy to add new building types:
            # 'solar_panel': {
            #     'component_class': SolarPanelComponent,
            #     'size': (1, 1),
            #     'preview_color': (255, 255, 0),
            #     'walkable': True,
            # },
        }

    def start_placement(self, building_type: str) -> bool:
        """Start placing a specific type of building"""
        if building_type not in self.building_types:
            return False
        self.current_building_type = building_type
        self.is_placing = True
        return True

    def cancel_placement(self):
        """Cancel current building placement"""
        self.is_placing = False
        self.current_building_type = None
        self.ghost_position = None
        
    def handle_event(self, event) -> bool:
        """Handle build-related events"""
        if not self.is_placing or not self.current_building_type:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.ghost_valid:
                self._place_building()
                return True
                
        elif event.type == pygame.MOUSEMOTION:
            self._update_ghost_position(event.pos)
            return True
            
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.cancel_placement()
            return True
            
        return False
        
    def _update_ghost_position(self, mouse_pos):
        """Updates the ghost building position based on mouse coordinates"""
        tile_x = int((mouse_pos[0] / self.game_state.zoom_level + self.game_state.camera_x) // TILE_SIZE)
        tile_y = int((mouse_pos[1] / self.game_state.zoom_level + self.game_state.camera_y) // TILE_SIZE)
        self.ghost_position = (tile_x, tile_y)
        self.ghost_valid = self._is_valid_position(tile_x, tile_y)
        
    def _is_valid_position(self, x, y) -> bool:
        """Check if area is valid for building placement"""
        if not self.current_building_type:
            return False
            
        building_info = self.building_types[self.current_building_type]
        size = building_info['size']
        tilemap = self.game_state.current_level.tilemap
        
        # Check bounds
        if not (0 <= x < tilemap.width - size[0] + 1 and 
                0 <= y < tilemap.height - size[1] + 1):
            return False
            
        # Check area
        for dx in range(size[0]):
            for dy in range(size[1]):
                check_x = x + dx
                check_y = y + dy
                if not tilemap.is_walkable(check_x, check_y) or \
                   tilemap.get_electrical(check_x, check_y):
                    return False
                    
        return True
        
    def _place_building(self) -> bool:
        """Place a new building at the ghost position"""
        if not self.ghost_valid or not self.ghost_position or not self.current_building_type:
            return False
            
        building_info = self.building_types[self.current_building_type]
        x, y = self.ghost_position
        
        # Create entity with proper x,y coordinates in world space
        world_x = x * TILE_SIZE
        world_y = y * TILE_SIZE
        entity = Entity(world_x, world_y)  # Make sure Entity.__init__ accepts these parameters
        entity.x = world_x  # Explicitly set coordinates
        entity.y = world_y
        entity.game_state = self.game_state
        
        # Create building component
        component_class = building_info['component_class']
        building = component_class(entity)
        building.type = self.current_building_type
        
        # Add to tilemap for all required tiles
        size = building_info['size']
        for dx in range(size[0]):
            for dy in range(size[1]):
                pos = (x + dx, y + dy)
                self.game_state.current_level.tilemap.add_electrical(pos, building)
                
        return True
        
    def draw(self, surface):
        """Render ghost preview for building placement"""
        if not self.is_placing or not self.current_building_type or not self.ghost_position:
            return
            
        building_info = self.building_types[self.current_building_type]
        size = building_info['size']
        preview_color = building_info['preview_color']
            
        # Calculate screen position
        zoom = self.game_state.zoom_level
        screen_x = (self.ghost_position[0] * TILE_SIZE - self.game_state.camera_x) * zoom
        screen_y = (self.ghost_position[1] * TILE_SIZE - self.game_state.camera_y) * zoom
        total_size = TILE_SIZE * size[0] * zoom
        
        # Draw ghost outline
        color = (0, 255, 0, 128) if self.ghost_valid else (255, 0, 0, 128)
        ghost_surface = pygame.Surface((total_size, total_size), pygame.SRCALPHA)
        pygame.draw.rect(ghost_surface, color, (0, 0, total_size, total_size), max(1, int(2 * zoom)))
        
        # Draw simplified building preview
        if self.ghost_valid:
            preview_color = (*preview_color, 64)  # Add transparency
            pygame.draw.rect(ghost_surface, preview_color,
                           (total_size * 0.2, total_size * 0.2, 
                            total_size * 0.6, total_size * 0.6))
            
        surface.blit(ghost_surface, (screen_x, screen_y)) 

    def place_building(self) -> bool:
        """Public interface for placing a building"""
        return self._place_building() 