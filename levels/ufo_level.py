from .base_level import BaseLevel
from entities.alien import Alien
from utils.config import *
from core.tiles import TILE_FLOOR, TILE_WALL, TILE_BARRIER

class UfoLevel(BaseLevel):
    def initialize(self):
        # Create UFO layout
        self._create_ufo_map()
        
        # Create crew positions
        center_x = MAP_WIDTH // 2
        center_y = MAP_HEIGHT // 2
        
        # Create aliens in UFO bridge positions
        crew_positions = [
            (center_x, center_y),      # Captain (pink)
            (center_x - 2, center_y),  # Navigation (blue)
            (center_x + 2, center_y),  # Weapons (green)
            (center_x, center_y - 2),  # Science (purple)
            (center_x, center_y + 2),  # Engineering (orange)
        ]
        
        crew_colors = [
            (255, 192, 203, 128),  # Pink
            (100, 149, 237, 128),  # Blue
            (144, 238, 144, 128),  # Green
            (147, 112, 219, 128),  # Purple
            (255, 165, 0, 128),    # Orange
        ]
        
        for pos, color in zip(crew_positions, crew_colors):
            alien = Alien(pos[0], pos[1], color)
            alien.game_state = self.game_state
            self.aliens.append(alien)
            self.entity_manager.add_entity(alien)
    
    def _create_ufo_map(self):
        # Fill with floor tiles
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                self.tilemap.set_tile(x, y, TILE_FLOOR.name)
        
        # Create circular UFO shape
        center_x = MAP_WIDTH // 2
        center_y = MAP_HEIGHT // 2
        radius = min(MAP_WIDTH, MAP_HEIGHT) // 3
        
        # Add walls for UFO outline
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                dx = x - center_x
                dy = y - center_y
                distance = (dx * dx + dy * dy) ** 0.5
                
                # Create circular wall boundary
                if abs(distance - radius) < 1.5:
                    self.tilemap.set_tile(x, y, TILE_WALL.name)
                # Make outside of UFO unwalkable
                elif distance > radius:
                    self.tilemap.set_tile(x, y, TILE_BARRIER.name)
    
    def update(self, dt):
        self.entity_manager.update(dt) 