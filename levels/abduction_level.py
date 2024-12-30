from .base_level import BaseLevel
from entities.alien import Alien
from utils.config import *
from core.tiles import TILE_GRASS, TILE_ROCK, TILE_WALL, TILE_BARRIER
import random

class AbductionLevel(BaseLevel):
    def initialize(self):
        # Create the current map layout with grass, rocks, and barriers
        self._create_abduction_map()
        
        # Create aliens in their starting positions
        center_x = MAP_WIDTH // 2
        center_y = MAP_HEIGHT // 2
        
        # Create aliens with their colors
        alien_configs = [
            (center_x, center_y, (255, 192, 203, 128)),      # Pink (center)
            (center_x - 2, center_y - 2, (100, 149, 237, 128)),  # Blue
            (center_x + 2, center_y - 2, (144, 238, 144, 128)),  # Green
            (center_x - 2, center_y + 2, (147, 112, 219, 128)),  # Purple
            (center_x + 2, center_y + 2, (255, 165, 0, 128))     # Orange
        ]
        
        for x, y, color in alien_configs:
            alien = Alien(x, y, color)
            alien.game_state = self.game_state
            self.aliens.append(alien)
            self.entity_manager.add_entity(alien)
    
    def _create_abduction_map(self):
        # Fill with grass (green)
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                self.tilemap.set_tile(x, y, TILE_GRASS.name)
        
        # Add random rocks (brown)
        for _ in range(MAP_WIDTH * MAP_HEIGHT // 10):  # 10% of tiles
            x = random.randint(0, MAP_WIDTH - 1)
            y = random.randint(0, MAP_HEIGHT - 1)
            if (x, y) != (MAP_WIDTH // 2, MAP_HEIGHT // 2):  # Don't place on spawn
                self.tilemap.set_tile(x, y, TILE_ROCK.name)
        
        # Add barriers (red zones)
        barrier_positions = [
            (5, 5), (5, MAP_HEIGHT - 6),
            (MAP_WIDTH - 6, 5), (MAP_WIDTH - 6, MAP_HEIGHT - 6)
        ]
        
        for bx, by in barrier_positions:
            for dx in range(3):
                for dy in range(3):
                    self.tilemap.set_tile(bx + dx, by + dy, TILE_BARRIER.name)
        
        # Add vertical barriers (gray)
        for y in range(MAP_HEIGHT):
            self.tilemap.set_tile(MAP_WIDTH // 3, y, TILE_WALL.name)
            self.tilemap.set_tile(2 * MAP_WIDTH // 3, y, TILE_WALL.name)
    
    def update(self, dt):
        self.entity_manager.update(dt) 